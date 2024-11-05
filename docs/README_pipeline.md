# Data Ingestion Pipeline

This repository contains a data ingestion pipeline implemented with [Dagster](https://dagster.io/). The pipeline fetches data from specified endpoints and loads it into a SQLite database. The pipeline is configured with a daily schedule.

## Prerequisites

- Python 3.8 or higher
- [Dagster](https://docs.dagster.io/getting-started) installed
- SQLite (included with Python)
  
Install the required dependencies by running:

```bash
pip install -r requirements.txt
```
---


## Project Structure
Under src/data_ingestion_pipeline, you will find the following files:
- **assets.py**: Contains the individual assets (`fetch_*` and `load_*`) for fetching and loading data.
- **jobs.py**: Defines `data_ingestion_job`, a Dagster job that runs the entire data ingestion process.
- **schedules.py**: Defines the schedule for running the pipeline daily.
- **pipelines.py**: Sets up the Dagster repository, including the job and schedule.


## Setup and Configuration

1. **Database Setup**:
   - The pipeline writes data to a SQLite database at `data/recommendation_system.db`. Ensure the `data` directory exists in the project root.

   ```bash
   mkdir -p data
   ```
---



## Running the Pipeline Locally

You can execute the pipeline directly through Dagster’s CLI or through the `dagit` UI.

### 1. Run Pipeline via CLI

To run the `data_ingestion_job` pipeline manually from the command line:

```bash
dagster job execute -m data_ingestion_pipeline.jobs -j data_ingestion_job
```


### 2. Run Pipeline via Dagit UI

To start the Dagster UI and run the pipeline:

```bash
dagit -m data_ingestion_pipeline
```

## Running the Pipeline on a Schedule

The pipeline includes a daily schedule (`daily_data_ingestion_schedule`) set to run at midnight UTC. 

1. To activate the schedule, start the Dagster Daemon, which monitors and triggers scheduled jobs:

   ```bash
   dagster-daemon run
   ```
   
## Testing

To run tests for the pipeline:

```bash
 
pytest test/
```

## Troubleshooting

- **Database Errors**: Ensure that the SQLite database file (`data/recommendation_system.db`) is writable and accessible.
- **Environment Variable Issues**: Verify that any required environment variables are properly set in your environment.
   - if the error /ModuleNotFoundError: No module named 'src'/ occurs when running tests run this command to add src to your PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"  
```