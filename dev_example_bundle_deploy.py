# Databricks notebook source
# DBTITLE 1,Widgets, imports and sanity check
import os, subprocess
import json
from py4j.protocol import Py4JError
import urllib.request, zipfile

dbutils.widgets.text("path_to_bundle", "./default_python", label="Path to Bundle")
dbutils.widgets.text("databricks_cli_version", "0.243.0", label="Databricks CLI Version (refer to https://github.com/databricks/cli/releases)")
dbutils.widgets.dropdown("bundle_action", "validate", ["deploy", "destroy", "validate"], label="Databricks Asset Bundle Action")
dbutils.widgets.dropdown("bundle_auto_approve_deletes", "true", ["true", "false"], label="Auto Approve Deletes (when using destroy)")

path_to_bundle = dbutils.widgets.get("path_to_bundle")
bundle_action = dbutils.widgets.get("bundle_action")
databricks_cli_version = dbutils.widgets.get("databricks_cli_version")
bundle_auto_approve_deletes = dbutils.widgets.get("bundle_auto_approve_deletes") == "true"

try:
    context = json.loads(dbutils.entry_point.getDbutils().notebook().getContext().toJson())
except Py4JError as e:
    raise Exception("This notebook is only supported on single user 'Dedicated' clusters such as personal compute.")

# COMMAND ----------

# DBTITLE 1,Install the Databricks CLI
databricks_cli_root = f"/local_disk0/databricks_{databricks_cli_version}/"
databricks_cli_path = f"{databricks_cli_root}/databricks"

# Download the Databricks CLI if it doesn't exist already.
if not os.path.exists(databricks_cli_path):
    print(f"Installing Databricks CLI {databricks_cli_version}...")
    url = f"https://github.com/databricks/cli/releases/download/v{databricks_cli_version}/databricks_cli_{databricks_cli_version}_linux_amd64.zip"
    zip_path = f"{databricks_cli_root}/databricks_cli.zip"
    os.makedirs(databricks_cli_root, exist_ok=True)
    urllib.request.urlretrieve(url, zip_path)
    subprocess.run(["unzip", zip_path, "-d", databricks_cli_root], check=True)

# COMMAND ----------

# DBTITLE 1,Development Bundle Deploy
databricks_env = os.environ.copy()
databricks_env["DATABRICKS_TOKEN"] = context["extraContext"]["api_token"]
databricks_env["DATABRICKS_HOST"] = context["tags"]["browserHostName"]
result = subprocess.run([databricks_cli_path, "version"], cwd=path_to_bundle, env=databricks_env)

if result.returncode != 0:
    raise Exception("We were unable to run the Databricks CLI, are you running in single user mode and have direct access Github releases to download the Databricks CLI?")

# We're only deploying development here, as this script is not supported in production.
# Consider using CI/CD bundles if you want to depend on this method working consistently.
# https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/ci-cd-bundles
environment = "dev"
databricks_cli_commands = [databricks_cli_path, "bundle", bundle_action, "-t", environment, ] + (["--auto-approve"] if bundle_auto_approve_deletes else [])
result = subprocess.run(databricks_cli_commands,
                         cwd=path_to_bundle, env=databricks_env)

if result.returncode != 0:
    # It doesn't seem stderr is captured seperately than stdout, so we can't do anything clever like throwing an exception with the stderr text.
    raise Exception("Something went wrong during deployment, check the output messages of the bundle execution, resolve the errors and try again")
