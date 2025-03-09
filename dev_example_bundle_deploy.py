# Databricks notebook source
# DBTITLE 1,Development Bundle Deploy
import os
import json
import subprocess
from py4j.protocol import Py4JError

dbutils.widgets.text("path_to_bundle", "./default_python")
dbutils.widgets.dropdown("bundle_action", "validate", ["deploy", "destroy", "validate"])
path_to_bundle = dbutils.widgets.get("path_to_bundle")
bundle_action = dbutils.widgets.get("bundle_action")

try:
    context = json.loads(dbutils.entry_point.getDbutils().notebook().getContext().toJson())
except Py4JError as e:
    raise Exception("This notebook is only supported on single user 'Dedicated' clusters such as personal compute.")

databricks_env = os.environ.copy()
databricks_env["ENABLE_DATABRICKS_CLI"] = "true"
databricks_env["DATABRICKS_TOKEN"] = context["extraContext"]["api_token"]
databricks_env["DATABRICKS_HOST"] = context["tags"]["browserHostName"]

# This should never be any production environment. 
# This notebook serves only to support developers in releasing bundles within the same coding loop of updating notebooks/YAML files within Databricks Workspaces.
environment = "dev"

result = subprocess.run(["databricks", "version"], cwd=path_to_bundle, env=databricks_env)

if result.returncode != 0:
    raise Exception("We were unable to run the Databricks CLI, are you running in single user mode and have direct access Github releases to download the Databricks CLI?")

# We're only deploying development here, as this script is not supported in production.
# Consider using CI/CD bundles if you want to depend on this method working consistently.
# https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/ci-cd-bundles
result = subprocess.run(["databricks", "bundle", bundle_action, "-t", environment],
                         cwd=path_to_bundle, env=databricks_env)

if result.returncode != 0:
    # It doesn't seem stderr is captured seperately than stdout, so we can't do anything clever like throwing an exception with the stderr text.
    raise Exception("Something went wrong during deployment, check the output messages of the bundle execution, resolve the errors and try again")
