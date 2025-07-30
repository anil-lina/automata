import oracledb
import json
from dagster import asset, Definitions, Output
from src.utils.config import get_oracle_credentials, get_table_configs
from src.utils.state_manager import get_last_timestamp, update_last_timestamp
from datetime import datetime

def build_oracle_asset(table_name, is_incremental, cursor_column):
    @asset(name=f"oracle_{table_name}")
    def _oracle_asset(context):
        """
        Connects to an Oracle database, fetches data from the specified table in chunks,
        and yields a separate JSON string for each chunk.
        """
        creds = get_oracle_credentials()
        connection = oracledb.connect(user=creds["user"], password=creds["password"], dsn=creds["dsn"])

        if is_incremental:
            last_timestamp = get_last_timestamp(table_name)
            query = f"SELECT * FROM {table_name} WHERE {cursor_column} > TO_TIMESTAMP('{last_timestamp}', 'YYYY-MM-DD HH24:MI:SS')"
        else:
            query = f"SELECT * FROM {table_name}"

        context.log.info(f"Executing query for table {table_name}: {query}")

        max_timestamp = None

        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            while True:
                rows = cursor.fetchmany(300000)
                if not rows:
                    break
                data = [dict(zip(columns, row)) for row in rows]
                if is_incremental:
                    for row in data:
                        if max_timestamp is None or row[cursor_column] > max_timestamp:
                            max_timestamp = row[cursor_column]
                yield Output(json.dumps(data, indent=4))

        connection.close()

        if is_incremental and max_timestamp:
            update_last_timestamp(table_name, max_timestamp)
            context.log.info(f"Updated last timestamp for table {table_name} to {max_timestamp}.")

    return _oracle_asset

def load_oracle_assets():
    table_configs = get_table_configs()
    return [build_oracle_asset(config["name"], config["incremental"], config.get("cursor_column")) for config in table_configs]
