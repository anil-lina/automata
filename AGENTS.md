## About This Project

This project is a Dagster data pipeline that extracts data from an Oracle database and loads it into an OCI Object Storage bucket. It uses dynamic assets to process multiple tables in parallel and supports incremental loading.

### Project Structure

- **`src/`**: Contains the main source code for the pipeline.
  - **`assets/`**: Contains the Dagster assets.
    - `oracle.py`: Dynamic asset for extracting data from Oracle. It generates a dynamic asset for each table defined in `tables.yaml`.
    - `oci.py`: Dynamic asset for uploading data to OCI.
  - **`jobs/`**: Contains the Dagster jobs.
    - `all_assets_job.py`: A job that materializes all dynamic assets.
  - **`sensors/`**: Contains the Dagster sensors and schedules.
    - `daily_trigger.py`: A daily schedule for the `all_assets_job`.
  - **`utils/`**: Contains utility functions.
    - `config.py`: Handles configuration and sensitive data, including loading the `tables.yaml` file.
    - `state_manager.py`: Manages the state for incremental loading.
  - **`definitions.py`**: The main entry point for Dagster, where all assets, jobs, and schedules are defined.
- **`tests/`**: Contains tests for the pipeline.
- **`.env.example`**: An example file for environment variables.
- **`requirements.txt`**: A list of Python dependencies.
- **`README.md`**: Instructions for setting up and running the project.
- **`tables.yaml`**: Configuration file for the tables to be processed.
- **`dagster.yaml`**: Configuration file for Dagster, including the run launcher for parallel execution.
- **`state.json`**: File for storing the state of incremental loads.

### How to Make Changes

- **Adding a new table**: Add a new entry to the `tables.yaml` file.
- **Changing the schedule**: Modify the schedule definition in `src/sensors/daily_trigger.py`.
- **Updating dependencies**: Add the new dependency to `requirements.txt`.
- **Modifying the extraction or loading logic**: The core logic for extraction and loading is in `src/assets/oracle.py` and `src/assets/oci.py` respectively.

### Running Tests

This project does not currently have any tests. If you add new features, please also add corresponding tests in the `tests/` directory.
