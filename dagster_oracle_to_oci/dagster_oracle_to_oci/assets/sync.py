import os
import json
import yaml
from datetime import datetime
from pathlib import Path
import tempfile

from dagster import asset, Config, AssetExecutionContext, DagsterInvariantViolationError
import oracledb
from oci.object_storage import ObjectStorageClient, UploadManager

class SyncConfig(Config):
    """
    Configuration for the oracle_to_oci_sync asset.

    Attributes:
        tables_config_path (str): Path to the YAML file with table configurations.
        oci_bucket (str): Name of the OCI bucket.
        state_dir (str): Directory to store state files. Defaults to "state".
    """
    tables_config_path: str
    oci_bucket: str
    state_dir: str = "state"

def get_last_incremental_value(state_dir: Path, table_name: str) -> any:
    """Reads the last incremental value from the state file."""
    state_file = state_dir / f"{table_name}.json"
    if state_file.exists():
        with open(state_file, 'r') as f:
            state_data = json.load(f)
            return state_data.get("last_incremental_value")
    return None

def save_last_incremental_value(state_dir: Path, table_name: str, value: any):
    """Saves the last incremental value to the state file."""
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_dir / f"{table_name}.json"
    with open(state_file, 'w') as f:
        json.dump({"last_incremental_value": value}, f, default=str)

@asset(
    name="oracle_to_oci_sync",
    description="Syncs tables from Oracle to OCI Object Storage.",
    required_resource_keys={"oracle", "oci"},
)
def sync_asset(context: AssetExecutionContext, config: SyncConfig, oracle: oracledb.Connection, oci: ObjectStorageClient):
    """
    This asset connects to an Oracle DB, retrieves data in chunks,
    and uploads it to an OCI bucket as JSON files.
    """
    # Load table configurations from YAML
    with open(config.tables_config_path, 'r') as f:
        tables_config = yaml.safe_load(f)

    tables = tables_config.get("tables", [])
    if len(tables) > 2:
        raise DagsterInvariantViolationError(
            f"This asset is configured to handle a maximum of 2 tables per run, but {len(tables)} were provided."
        )

    oci_bucket = config.oci_bucket
    state_dir = Path(config.state_dir)

    namespace = oci.get_namespace().data
    upload_manager = UploadManager(oci)

    for table_info in tables:
        table_name = table_info["name"]
        is_incremental = table_info.get("incremental", False)
        incremental_column = table_info.get("incremental_column")

        context.log.info(f"Processing table: {table_name}")

        # Build query
        query = f"SELECT * FROM {table_name}"
        last_inc_value = None
        if is_incremental and incremental_column:
            last_inc_value = get_last_incremental_value(state_dir, table_name)
            if last_inc_value:
                # Using bind variables for security and correctness
                query += f" WHERE {incremental_column} > :last_inc_value"
            query += f" ORDER BY {incremental_column}"

        cursor = oracle.cursor()
        if last_inc_value:
            cursor.execute(query, last_inc_value=last_inc_value)
        else:
            cursor.execute(query)

        cursor.arraysize = 300000
        columns = [col[0] for col in cursor.description]

        max_incremental_value = last_inc_value

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            while True:
                rows = cursor.fetchmany()
                if not rows:
                    break

                context.log.info(f"Fetched {len(rows)} rows from {table_name}.")
                data = [dict(zip(columns, row)) for row in rows]

                if is_incremental and incremental_column and data:
                    # Convert to string for comparison to handle both numbers and dates uniformly
                    current_max = max(str(row[incremental_column]) for row in data if row[incremental_column] is not None)
                    if max_incremental_value is None or current_max > str(max_incremental_value):
                        max_incremental_value = current_max

                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                file_name = f"{timestamp}_{table_name}_{len(data)}.json"
                local_file_path = temp_path / file_name

                with open(local_file_path, 'w') as f:
                    json.dump(data, f, default=str)

                context.log.info(f"Wrote data to {local_file_path}")

                context.log.info(f"Uploading {file_name} to OCI bucket {oci_bucket}...")
                upload_manager.upload_file(
                    namespace_name=namespace,
                    bucket_name=oci_bucket,
                    object_name=file_name,
                    file_path=str(local_file_path)
                )
                context.log.info(f"Successfully uploaded {file_name}.")

            if is_incremental and max_incremental_value is not None and max_incremental_value != last_inc_value:
                save_last_incremental_value(state_dir, table_name, max_incremental_value)
                context.log.info(f"Saved max incremental value for {table_name}: {max_incremental_value}")

        cursor.close()
    context.log.info("Sync complete.")
