# AI-Lab 5.0.0 released 2026-04-20

Code name: Password Override and UI Refactor

## Summary

This release supports overriding the default password by passing an environment variable when running the Docker container. See the [User guide](https://github.com/exasol/ai-lab/blob/main/doc/user_guide/docker/docker-usage.md) for details.
This release replaces Jupyter UI imports with normal Python imports from `exasol-notebook-connector`.

### Example: Replace Jupyter UI notebooks with Python imports

Let see example code snippets to demonstrate the replacement of Jupyter UI notebooks with standard Python imports from `exasol-notebook-connector`.
we will import access store and JupySQL initialization code, which were previously imported via `%run` in the notebooks.
#### Example 1: Open secure configuration store
The `access_store` notebook was earlier imported via `%run`like below:

```python
%run utils/access_store_ui.ipynb
```

Now we can directly import the `access_store` from `exasol-notebook-connector` like below:
```python
from exasol.nb_connector.ui.access import access_store
from Ipython.display import display
# get access store instance
display(access_store.get_access_store())
```
#### Example 2: Initializing JupySQL
The `jupysql_init` notebook was earlier imported via `%run`like below:
```python
%run ../utils/jupysql_init.ipynb
```
Now we can directly import and initialize `jupysql` from `exasol-notebook-connector` like below:
```python
from exasol.nb_connector.ui.common import jupysql
# Initialize JupySQL with the loaded configuration
# For this example, assume `ai_lab_config` secret is already loaded
jupysql.init(ai_lab_config)
```

## Features

* #438: Added GPU Resource Considerations Notebook
* #440: Re-enabled Parquet import in notebook `first_steps.ipynb`
* #434: Supported overriding the default password when running the AI Lab Docker container
* #462: Adapted SLC notebooks to ScriptLanguageContainer changes
* #449: Added notebook to demonstrate PyExasol's import and export with Polars and PyArrow
* #480: Added JupySql quickstart notebook

## Security Issues

* #452: Fixed vulnerability CVE-2024-48908 by updating GitHub action `lycheeverse/lychee-action@v1.9.0`
* Fixed CVE-2025-66471 (urllib3)
* Fixed CVE-2025-68146 (filelock)
* Fixed CVE-2025-59842 (jupyterlab)

## Documentation

* #432: Fixed structure and links in notebook first-steps
* #337: Ensured correct spelling for AI Lab
* #441: Added section "Getting Started" to User Guide

## Refactorings

* #458: Switched docker hub credentials
* #460: Updated notebook-connector
* #482: Updated `exasol-notebook-connector` version to support python import for UI notebooks
* #487: Replaced UI notebooks with standard Python imports from `exasol-notebook-connector`
* #492: Fixed vulnerabilities by updating dependencies