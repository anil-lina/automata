import oci
from dagster import asset
from src.utils.config import get_oci_config, get_oci_bucket_info, get_table_configs
import pandas as pd
from io import StringIO

def build_oci_asset(table_name):
    @asset(name=f"oci_upload_{table_name}", deps=[f"oracle_{table_name}"])
    def _oci_asset(context, oracle_data: pd.DataFrame):
        """
        Uploads a Pandas DataFrame to an OCI Object Storage bucket as a CSV file.
        """
        config = get_oci_config()
        bucket_info = get_oci_bucket_info()
        object_storage = oci.object_storage.ObjectStorageClient(config)

        if not oracle_data.empty:
            csv_buffer = StringIO()
            oracle_data.to_csv(csv_buffer, index=False)

            object_name = f"{table_name}_data_from_oracle.csv"

            object_storage.put_object(
                namespace_name=bucket_info["namespace"],
                bucket_name=bucket_info["bucket_name"],
                object_name=object_name,
                put_object_body=csv_buffer.getvalue()
            )
            context.log.info(f"Uploaded {object_name} to OCI bucket {bucket_info['bucket_name']}.")
        else:
            context.log.info(f"No new data for table {table_name}. Skipping upload.")
    return _oci_asset

def load_oci_assets():
    table_configs = get_table_configs()
    return [build_oci_asset(config["name"]) for config in table_configs]
