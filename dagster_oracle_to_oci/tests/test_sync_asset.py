import pytest
from unittest.mock import MagicMock, patch, mock_open
import oracledb
from oci.object_storage import ObjectStorageClient

from dagster import build_asset_context
from pathlib import Path
import yaml
import json

from dagster_oracle_to_oci.assets.sync import sync_asset, SyncConfig

@pytest.fixture
def mock_oracle_connection():
    """Mocks the Oracle connection and cursor."""
    mock_conn = MagicMock(spec=oracledb.Connection)
    mock_cursor = MagicMock()

    # Sample data to be "fetched"
    mock_cursor.description = [('ID',), ('NAME',)]
    mock_cursor.fetchmany.side_effect = [
        [(1, 'Product A'), (2, 'Product B')],
        [] # End of data
    ]

    mock_conn.cursor.return_value = mock_cursor
    return mock_conn

@pytest.fixture
def mock_oci_client():
    """Mocks the OCI ObjectStorageClient."""
    mock_client = MagicMock(spec=ObjectStorageClient)
    # The namespace in the oci client is not a string, but an object with a data attribute
    mock_namespace_obj = MagicMock()
    mock_namespace_obj.data = "test_namespace"
    mock_client.get_namespace.return_value = mock_namespace_obj
    return mock_client

def test_sync_asset_full_load(tmp_path, mock_oracle_connection, mock_oci_client):
    """Tests the sync_asset for a full load scenario."""
    # Create a dummy config file
    config_data = {
        "tables": [
            {"name": "PRODUCTS", "incremental": False}
        ]
    }
    config_file = tmp_path / "tables.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    # Create SyncConfig instance
    sync_config = SyncConfig(
        tables_config_path=str(config_file),
        oci_bucket="test-bucket",
        state_dir=str(tmp_path / "state")
    )

    # Build asset context
    context = build_asset_context(
        resources={
            "oracle": mock_oracle_connection,
            "oci": mock_oci_client,
        }
    )

    # Run the asset
    sync_asset(context=context, config=sync_config, oracle=mock_oracle_connection, oci=mock_oci_client)

    # Assertions
    mock_oci_client.put_object.assert_called_once()

    args, kwargs = mock_oci_client.put_object.call_args
    assert kwargs['bucket_name'] == "test-bucket"
    assert kwargs['namespace_name'] == "test_namespace"
    assert kwargs['object_name'].endswith("_PRODUCTS_2.json")

    state_dir = tmp_path / "state"
    assert not state_dir.exists()

def test_sync_asset_incremental_load(tmp_path, mock_oracle_connection, mock_oci_client):
    """Tests the sync_asset for an incremental load scenario."""
    config_data = {
        "tables": [
            {"name": "CUSTOMERS", "incremental": True, "incremental_column": "ID"}
        ]
    }
    config_file = tmp_path / "tables.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    mock_cursor = MagicMock()
    mock_cursor.description = [('ID',), ('NAME',)]
    mock_cursor.fetchmany.side_effect = [
        [(3, 'Customer C'), (4, 'Customer D')],
        []
    ]
    mock_oracle_connection.cursor.return_value = mock_cursor

    state_dir = tmp_path / "state"
    state_dir.mkdir()
    state_file = state_dir / "CUSTOMERS.json"
    with open(state_file, 'w') as f:
        json.dump({"last_incremental_value": 2}, f)

    sync_config = SyncConfig(
        tables_config_path=str(config_file),
        oci_bucket="test-bucket",
        state_dir=str(state_dir)
    )

    context = build_asset_context(
        resources={
            "oracle": mock_oracle_connection,
            "oci": mock_oci_client,
        }
    )

    sync_asset(context=context, config=sync_config, oracle=mock_oracle_connection, oci=mock_oci_client)

    mock_oracle_connection.cursor().execute.assert_called_with(
        "SELECT * FROM CUSTOMERS WHERE ID > :last_inc_value ORDER BY ID",
        last_inc_value=2
    )

    mock_oci_client.put_object.assert_called_once()

    with open(state_file, 'r') as f:
        new_state = json.load(f)
    assert new_state["last_incremental_value"] == 4
