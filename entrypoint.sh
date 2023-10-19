#!/bin/bash

## Initialize great_expectations if not initialized
if [ ! -d "great_expectations" ]; then
    yes | great_expectations init
fi

# Create a dataset and define the expectation
python3 test_expectations_infousers_username.py

# Run great_expectations for validation
yes | great_expectations docs build

# Execute dbt
cd dbt_project/ && dbt deps
dbt run -m models/my_model.sql
dbt test

# Keep the container running
tail -f /dev/null
