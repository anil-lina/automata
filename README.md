# Oracle to OCI Data Pipeline

This project is a Dagster-based data pipeline that extracts data from an Oracle database and uploads it to an OCI Object Storage bucket. It supports incremental loading for multiple tables and executes the jobs in parallel.

## Features

- **Incremental Loading:** The pipeline can perform incremental loads for specified tables based on a `PROCESSED_DTTM` timestamp column.
- **Parallel Execution:** The pipeline can process multiple tables in parallel, significantly reducing the overall execution time.
- **Dynamic Assets:** The pipeline uses Dagster's dynamic assets to create a separate asset for each table, allowing for flexible and scalable data processing.
- **Configuration-driven:** The tables to be processed are defined in a simple YAML file.

## Prerequisites

- Python 3.8+
- An Oracle database
- An OCI account with an Object Storage bucket

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the environment variables:**
   - Copy the `.env.example` file to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file and provide the necessary credentials and configuration for your Oracle database and OCI account.

5. **Configure the tables to process:**
   - Edit the `tables.yaml` file to define the tables you want to process.
   - For each table, you can specify `name` and `incremental` (true/false).

## Running the Pipeline

1. **Start the Dagster UI:**
   ```bash
   dagster-webserver -m src.definitions
   ```

2. **Open the Dagster UI:**
   Open your web browser and go to `http://localhost:3000`.

3. **Trigger the pipeline:**
   - In the Dagster UI, you can see the `all_assets_job` and the `daily_data_load_schedule`.
   - You can manually trigger a run of the `all_assets_job` from the UI.
   - The `daily_data_load_schedule` will automatically trigger a run every day at midnight.
