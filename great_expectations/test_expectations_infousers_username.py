import os
import great_expectations as gx
from great_expectations.checkpoint import Checkpoint

# Initialize the Great Expectations context
context = gx.get_context()

# Construct the PostgreSQL connection string from environment variables
PG_CONNECTION_STRING = f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"

# Add or update the SQL data source for PostgreSQL
pg_datasource = context.sources.add_or_update_sql(
    name="pg_datasource", connection_string=PG_CONNECTION_STRING
)

# Add the 'users_info' table as an asset for the data source
pg_datasource.add_table_asset(
    name="postgres_users_info_data", table_name="users_info"
)

# Build the batch request for the 'users_info' table
batch_request = pg_datasource.get_asset("postgres_users_info_data").build_batch_request()

# Define the expectation suite name
expectation_suite_name = "info_users_suite_expectations"

# Add or update the expectation suite in the context
context.add_or_update_expectation_suite(expectation_suite_name=expectation_suite_name)

# Get the validator for the data batch and expectation suite
validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name=expectation_suite_name,
)

# Set expectations: column 'username' should not have null values
validator.expect_column_values_to_not_be_null(column="username")

# Set expectations: column 'username' should not contain numeric characters
validator.expect_column_values_to_not_match_regex(column="username", regex="[0-9]")

# Save the defined expectations
validator.save_expectation_suite(discard_failed_expectations=False)

# Define the checkpoint name
my_checkpoint_name = "my_sql_checkpoint"

# Create and define a checkpoint
checkpoint = Checkpoint(
    name=my_checkpoint_name,
    run_name_template="%Y%m%d-%H%M%S-my-run-name-template",
    data_context=context,
    batch_request=batch_request,
    expectation_suite_name=expectation_suite_name,
    action_list=[
        {
            "name": "store_validation_result",
            "action": {"class_name": "StoreValidationResultAction"},
        },
        {"name": "update_data_docs", "action": {"class_name": "UpdateDataDocsAction"}},
    ],
)

# Add or update the defined checkpoint in the context
context.add_or_update_checkpoint(checkpoint=checkpoint)

# Run the checkpoint and store the results
checkpoint_result = checkpoint.run()
