import pytest
from unittest.mock import MagicMock, patch, mock_open
import oracledb
from oci.object_storage import ObjectStorageClient

from dagster import build_asset_context, DagsterInvariantViolationError
from pathlib import Path
import yaml
import json

from dagster_oracle_to_oci.assets.sync import sync_asset

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
    """Mocks the OCI ObjectStorageClient, needed for UploadManager init."""
    mock_client = MagicMock(spec=ObjectStorageClient)
    mock_namespace_obj = MagicMock()
    mock_namespace_obj.data = "test_namespace"
    mock_client.get_namespace.return_value = mock_namespace_obj
    return mock_client

@patch('dagster_oracle_to_oci.assets.sync.UploadManager')
@patch('dagster_oracle_to_oci.assets.sync.config')
def test_sync_asset_full_load(mock_config, mock_upload_manager_class, tmp_path, mock_oracle_connection, mock_oci_client):
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

    # Patch the config object
    mock_config.TABLES_CONFIG_PATH = str(config_file)
    mock_config.OCI_ASSET_BUCKET = "test-bucket"

    # Build asset context
    context = build_asset_context(
        resources={
            "oracle": mock_oracle_connection,
            "oci": mock_oci_client,
        }
    )

    # Run the asset
    sync_asset(context=context)

    # Assertions
    mock_upload_manager_instance = mock_upload_manager_class.return_value
    mock_upload_manager_instance.upload_file.assert_called_once()

    args, kwargs = mock_upload_manager_instance.upload_file.call_args
    assert kwargs['bucket_name'] == "test-bucket"
    assert kwargs['namespace_name'] == "test_namespace"
    assert kwargs['object_name'].endswith("_PRODUCTS_2.json")

    state_dir = tmp_path / "state"
    assert not state_dir.exists()

@patch('dagster_oracle_to_oci.assets.sync.UploadManager')
@patch('dagster_oracle_to_oci.assets.sync.config')
def test_sync_asset_incremental_load(mock_config, mock_upload_manager_class, tmp_path, mock_oracle_connection, mock_oci_client):
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

    # Note: the asset now hardcodes the state_dir to "state". We can't easily change it for a test
    # without also patching Path. We will assume the test runs in a context where "state" dir is ok.
    # For more complex scenarios, the state_dir could be made configurable on the resource.
    state_dir = Path("state")
    state_dir.mkdir(exist_ok=True)
    state_file = state_dir / "CUSTOMERS.json"
    with open(state_file, 'w') as f:
        json.dump({"last_incremental_value": 2}, f)

    mock_config.TABLES_CONFIG_PATH = str(config_file)
    mock_config.OCI_ASSET_BUCKET = "test-bucket"

    context = build_asset_context(
        resources={
            "oracle": mock_oracle_connection,
            "oci": mock_oci_client,
        }
    )

    sync_asset(context=context)

    mock_oracle_connection.cursor().execute.assert_called_with(
        "SELECT * FROM CUSTOMERS WHERE ID > :last_inc_value ORDER BY ID",
        last_inc_value=2
    )

    mock_upload_manager_instance = mock_upload_manager_class.return_value
    mock_upload_manager_instance.upload_file.assert_called_once()

    with open(state_file, 'r') as f:
        new_state = json.load(f)
    assert new_state["last_incremental_value"] == '4'

@patch('dagster_oracle_to_oci.assets.sync.config')
def test_sync_asset_too_many_tables(mock_config, tmp_path):
    """Tests that the asset fails if more than 2 tables are configured."""
    config_data = {
        "tables": [
            {"name": "TABLE1"},
            {"name": "TABLE2"},
            {"name": "TABLE3"},
        ]
    }
    config_file = tmp_path / "tables.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    mock_config.TABLES_CONFIG_PATH = str(config_file)

    context = build_asset_context(resources={"oracle": MagicMock(spec=oracledb.Connection), "oci": MagicMock(spec=ObjectStorageClient)})

    with pytest.raises(DagsterInvariantViolationError, match="maximum of 2 tables"):
        sync_asset(context=context)

@patch('dagster_oracle_to_oci.assets.sync.UploadManager')
@patch('dagster_oracle_to_oci.assets.sync.config')
def test_sync_asset_incremental_load_timestamp(mock_config, mock_upload_manager_class, tmp_path, mock_oracle_connection, mock_oci_client):
    """Tests the sync_asset for an incremental load scenario with timestamps."""
    from datetime import datetime
    config_data = {
        "tables": [
            {"name": "EVENTS", "incremental": True, "incremental_column": "EVENT_TIME", "incremental_column_type": "timestamp"}
        ]
    }
    config_file = tmp_path / "tables.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    mock_cursor = MagicMock()
    mock_cursor.description = [('ID',), ('EVENT_TIME',)]
    # Fetched data has newer timestamps
    mock_cursor.fetchmany.side_effect = [
        [(3, datetime(2025, 6, 22, 17, 0, 0)), (4, datetime(2025, 6, 22, 18, 0, 0))],
        []
    ]
    mock_oracle_connection.cursor.return_value = mock_cursor

    state_dir = Path("state")
    state_dir.mkdir(exist_ok=True)
    state_file = state_dir / "EVENTS.json"
    last_timestamp = datetime(2025, 6, 22, 16, 46, 3)
    # The state file will store the timestamp as a string, as per json.dump(default=str)
    with open(state_file, 'w') as f:
        json.dump({"last_incremental_value": str(last_timestamp)}, f)

    mock_config.TABLES_CONFIG_PATH = str(config_file)
    mock_config.OCI_ASSET_BUCKET = "test-bucket"

    context = build_asset_context(
        resources={
            "oracle": mock_oracle_connection,
            "oci": mock_oci_client,
        }
    )

    sync_asset(context=context)

    # Check that the query was filtered with the correct timestamp string
    mock_oracle_connection.cursor().execute.assert_called_with(
        "SELECT * FROM EVENTS WHERE EVENT_TIME > to_timestamp(:last_inc_value, 'YYYY-MM-DD HH24:MI:SS.FF6') ORDER BY EVENT_TIME",
        last_inc_value=str(last_timestamp)
    )

    mock_upload_manager_instance = mock_upload_manager_class.return_value
    mock_upload_manager_instance.upload_file.assert_called_once()

    # Check that the state file was updated with the new max timestamp
    with open(state_file, 'r') as f:
        new_state = json.load(f)
    assert new_state["last_incremental_value"] == str(datetime(2025, 6, 22, 18, 0, 0))
