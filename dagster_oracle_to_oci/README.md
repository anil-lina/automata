# Dagster Project: Oracle to OCI Sync

This Dagster project provides a robust and configurable solution for extracting data from an Oracle database, processing it, and uploading it to an Oracle Cloud Infrastructure (OCI) Object Storage bucket in JSON format.

## Features

- **Oracle to OCI**: Seamlessly transfers data from Oracle tables to OCI buckets.
- **Incremental Loading**: Supports both full and incremental data syncs. For incremental loads, it tracks the maximum value of a specified cursor column (including timestamps) to only fetch new data.
- **Efficient Chunking**: Retrieves data in large chunks (configurable, defaults to 300,000 rows) to handle large tables without consuming excessive memory.
- **Reliable Uploads**: Uses OCI's `UploadManager` to handle file uploads, providing multipart capabilities for large files and increased reliability.
- **Configuration-driven**: Define which tables to sync, their incremental settings, and connection details through simple YAML and `.env` files.
- **Scheduled Execution**: Includes an hourly schedule to automatically run the sync job.
- **Concurrency Control**: A safety check is included to limit a single run to processing a maximum of two tables.

## Prerequisites

- Python 3.8+
- An Oracle database and the necessary credentials.
- An OCI account with an Object Storage bucket and the required API credentials.
- The Oracle Instant Client libraries installed and configured on the machine running Dagster.

## Setup & Configuration

### 1. Install Dependencies

Clone this repository and navigate to the project root (`dagster_oracle_to_oci`). Install the project and its dependencies in editable mode:

```bash
pip install -e .
```

### 2. Configure Your Project

Configuration for this project is managed in two places:

1.  **`dagster_oracle_to_oci/config.py`**: This file sources required connection details and credentials from environment variables. For local development, you can create a `.env` file in the project root (`dagster_oracle_to_oci/.env`) to have these automatically loaded.
2.  **`config/tables.yaml`**: This file defines which tables the asset should process.

**`.env` template for local development:**

```dotenv
# Oracle Database Credentials
ORACLE_USER=your_oracle_username
ORACLE_PASSWORD=your_oracle_password
ORACLE_HOST=your_oracle_host.com
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=your_service_name

# OCI Credentials
OCI_USER_OCID=ocid1.user.oc1..your_user_ocid
OCI_FINGERPRINT=your_api_key_fingerprint
OCI_KEY_FILE=/path/to/your/oci_api_key.pem
OCI_TENANCY_OCID=ocid1.tenancy.oc1..your_tenancy_ocid
OCI_REGION=us-ashburn-1

# OCI Bucket for the Asset
OCI_BUCKET_NAME=your-target-bucket-name
```

### 3. Configure Tables

The `config/tables.yaml` file defines which tables to process. You can add or remove tables here.

**Example `config/tables.yaml`:**

```yaml
tables:
  - name: "CUSTOMERS"
    incremental: true
    incremental_column: "LAST_UPDATED" # Can be a timestamp or numeric ID
  - name: "PRODUCTS"
    incremental: false
```

**Note:** A single run of the job is limited to a maximum of 2 tables.

## Execution

### 1. Start the Dagster UI

From the project root (`dagster_oracle_to_oci`), run the following command:

```bash
dagster dev
```

This will start the Dagster webserver, typically available at `http://localhost:3000`.

### 2. Running the Job

- **Manual Runs**:
  - In the Dagster UI, navigate to the **Assets** tab.
  - Select the `oracle_to_oci_sync` asset and click **Materialize** to trigger a manual run. Since all configuration is now managed via `config.py` and `config/tables.yaml`, you can launch the run with empty configuration.

- **Scheduled Runs**:
  - The job is configured to run automatically every hour.
  - In the Dagster UI, navigate to the **Schedules** tab to view the status of the `hourly_schedule`. You can enable or disable the schedule from here.
