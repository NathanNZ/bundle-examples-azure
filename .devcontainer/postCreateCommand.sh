#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <localWorkspaceFolderBasename>"
    exit 1
fi

localWorkspaceFolderBasename="$1"

# Set ownership of important directories to vscode user
chown -R vscode:vscode /home/vscode

for dir in ".venv" ".databricks" "default_python/.databricks"; do
    target="/workspaces/${localWorkspaceFolderBasename}/${dir}"
    if [ -e "$target" ]; then
        chown -R vscode:vscode "$target"
    fi
done

echo "Success."