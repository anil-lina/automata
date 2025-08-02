import oracledb
from dagster import resource
from .. import config

@resource
def oracle_resource(_):
    """
    A Dagster resource for connecting to an Oracle database.
    It uses the configuration from the project's config.py file.
    """
    dsn = oracledb.makedsn(
        config.ORACLE_HOST,
        config.ORACLE_PORT,
        service_name=config.ORACLE_SERVICE_NAME,
    )

    connection = oracledb.connect(
        user=config.ORACLE_USER,
        password=config.ORACLE_PASSWORD,
        dsn=dsn
    )

    try:
        yield connection
    finally:
        connection.close()
