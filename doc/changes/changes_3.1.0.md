# AI-Lab 3.1.0 released 2024-09-10

Code name: Additional fixes on top of release 3.0.0

## Summary

This release updates jupyterlab to version `4.2.5`, applies some fixes to the Jupyter notebooks.

## Refactoring

* #324 Used pytest-plugins in notebook tests.

## Bug Fixes

* #326
  - Scikit-learn notebook: call model's fit and predict with numpy arrays;
  - Ibis notebook: added a link to this notebook on the front page;
  - Configuration: added internal bucket-fs host name and port;
  - Upgraded jupyterlab to 4.2.5.

## Dependency Updates

### `pyproject.toml`

* Updated dependency `boto3:1.35.2` to `1.35.11`
* Updated dependency `rich:13.7.1` to `13.8.0`
* Updated dependency `pygithub:2.3.0` to `2.4.0`
* Updated dependency `cfn-lint:1.10.3` to `1.12.1`
* Updated dependency `localstack:3.6.0` to `3.7.1`

### `jupyter_requirements.txt`

* Updated dependency `jupyterlab:4.1.1` to `4.2.5`

### `notebook_requirements.txt`

* Updated dependency `exasol-notebook-connector:0.2.9` to `0.3.0`
