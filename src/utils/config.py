import os
from dotenv import load_dotenv
import oci
import yaml

# Load environment variables from .env file
load_dotenv()

def get_oracle_credentials():
    """Returns Oracle database credentials from environment variables."""
    return {
        "user": os.getenv("ORACLE_USER"),
        "password": os.getenv("ORACLE_PASSWORD"),
        "dsn": os.getenv("ORACLE_DSN"),
    }

def get_oci_config():
    """Returns OCI configuration from environment variables."""
    config_path = os.path.expanduser(os.getenv("OCI_CONFIG_PATH", "~/.oci/config"))
    config_profile = os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
    return oci.config.from_file(file_location=config_path, profile_name=config_profile)

def get_oci_bucket_info():
    """Returns OCI bucket information from environment variables."""
    return {
        "bucket_name": os.getenv("OCI_BUCKET_NAME"),
        "namespace": os.getenv("OCI_NAMESPACE"),
    }

def get_table_configs():
    """Loads table configurations from tables.yaml."""
    with open("tables.yaml", "r") as f:
        return yaml.safe_load(f)
