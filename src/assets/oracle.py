import oracledb
import pandas as pd
from dagster import asset, Definitions
from src.utils.config import get_oracle_credentials, get_table_configs
from src.utils.state_manager import get_last_timestamp, update_last_timestamp
from datetime import datetime

def build_oracle_asset(table_name, is_incremental, cursor_column):
    @asset(name=f"oracle_{table_name}")
    def _oracle_asset(context):
        """
        Connects to an Oracle database, fetches data from the specified table,
        and returns it as a Pandas DataFrame.
        """
        creds = get_oracle_credentials()
        connection = oracledb.connect(user=creds["user"], password=creds["password"], dsn=creds["dsn"])

        if is_incremental:
            last_timestamp = get_last_timestamp(table_name)
            query = f"SELECT * FROM {table_name} WHERE {cursor_column} > TO_TIMESTAMP('{last_timestamp}', 'YYYY-MM-DD HH24:MI:SS')"
        else:
            query = f"SELECT * FROM {table_name}"

        context.log.info(f"Executing query for table {table_name}: {query}")

        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            df = pd.DataFrame(rows, columns=columns)

        connection.close()

        context.log.info(f"Fetched {len(df)} rows from table {table_name}.")

        if is_incremental and not df.empty:
            max_timestamp = df[cursor_column].max()
            update_last_timestamp(table_name, max_timestamp)
            context.log.info(f"Updated last timestamp for table {table_name} to {max_timestamp}.")

        return df
    return _oracle_asset

def load_oracle_assets():
    table_configs = get_table_configs()
    return [build_oracle_asset(config["name"], config["incremental"], config.get("cursor_column")) for config in table_configs]
