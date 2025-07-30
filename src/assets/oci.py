import oci
from dagster import asset, AssetIn
from src.utils.config import get_oci_config, get_oci_bucket_info, get_table_configs
import json
from datetime import datetime

def build_oci_asset(table_name):
    @asset(name=f"oci_upload_{table_name}", ins={"oracle_data": AssetIn(key=f"oracle_{table_name}")})
    def _oci_asset(context, oracle_data: str):
        """
        Uploads a JSON string to an OCI Object Storage bucket.
        """
        config = get_oci_config()
        bucket_info = get_oci_bucket_info()
        object_storage = oci.object_storage.ObjectStorageClient(config)

        if oracle_data:
            timestamp = datetime.now().strftime("%Y%m%d%H%M")
            object_name = f"{timestamp}_{table_name}.json"

            object_storage.put_object(
                namespace_name=bucket_info["namespace"],
                bucket_name=bucket_info["bucket_name"],
                object_name=object_name,
                put_object_body=oracle_data
            )
            context.log.info(f"Uploaded {object_name} to OCI bucket {bucket_info['bucket_name']}.")
        else:
            context.log.info(f"No new data for table {table_name}. Skipping upload.")
    return _oci_asset

def load_oci_assets():
    table_configs = get_table_configs()
    return [build_oci_asset(config["name"]) for config in table_configs]
