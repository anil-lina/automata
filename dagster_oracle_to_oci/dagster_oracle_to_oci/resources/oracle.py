import os
import oracledb
from dagster import resource, Field

@resource({
    "user": Field(str, description="Oracle username"),
    "password": Field(str, description="Oracle password"),
    "host": Field(str, description="Oracle host"),
    "port": Field(int, default_value=1521, description="Oracle port"),
    "service_name": Field(str, description="Oracle service name"),
})
def oracle_resource(context):
    """
    A Dagster resource for connecting to an Oracle database.
    """
    config = context.resource_config
    dsn = oracledb.makedsn(
        config["host"],
        config["port"],
        service_name=config["service_name"],
    )

    connection = oracledb.connect(
        user=config["user"],
        password=config["password"],
        dsn=dsn
    )

    try:
        yield connection
    finally:
        connection.close()
