## About This Project

This project is a Dagster data pipeline that extracts data from an Oracle database and loads it into an OCI Object Storage bucket. It uses asset factories to process multiple tables in parallel and supports incremental loading with a configurable cursor column. The data is chunked into files of 300,000 rows before being uploaded to OCI.

### Project Structure

- **`src/`**: Contains the main source code for the pipeline.
  - **`assets/`**: Contains the Dagster asset factories.
    - `oracle.py`: Asset factory for extracting data from Oracle. It generates an asset for each table defined in `tables.yaml`.
    - `oci.py`: Asset factory for uploading data to OCI.
  - **`sensors/`**: Contains the Dagster sensors and schedules.
    - `daily_trigger.py`: A schedule for the `all_assets_job`.
  - **`utils/`**: Contains utility functions.
    - `config.py`: Handles configuration and sensitive data, including loading the `tables.yaml` file.
    - `state_manager.py`: Manages the state for incremental loading. The state is stored in `state.json`.
  - **`definitions.py`**: The main entry point for Dagster, where all assets, jobs, and schedules are defined.
- **`tests/`**: Contains tests for the pipeline.
- **`.env.example`**: An example file for environment variables.
- **`requirements.txt`**: A list of Python dependencies.
- **`README.md`**: Instructions for setting up and running the project.
- **`tables.yaml`**: Configuration file for the tables to be processed. You can specify the `name`, `incremental` flag, and `cursor_column` for each table.
- **`dagster.yaml`**: Configuration file for Dagster, including the run launcher for parallel execution.
- **`state.json`**: File for storing the state of incremental loads.

### How to Make Changes

- **Adding a new table**: Add a new entry to the `tables.yaml` file.
- **Changing the schedule**: Modify the `cron_schedule` in `src/sensors/daily_trigger.py`.
- **Changing the chunk size**: Modify the chunk size in `src/assets/oci.py`.
- **Updating dependencies**: Add the new dependency to `requirements.txt`.
- **Modifying the extraction or loading logic**: The core logic for extraction and loading is in the asset factories in `src/assets/oracle.py` and `src/assets/oci.py` respectively.

### Running Tests

This project does not currently have any tests. If you add new features, please also add corresponding tests in the `tests/` directory.
