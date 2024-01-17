# data-science-sandbox 0.1.0, released t.b.d.

Code name: Initial release

## Summary

Initial release of the data-science-sandbox. It provides the creation of an Amazon Machine Image (AMI) and virtual machine images for a specific version of the data-science-sanbox-release project.

## Data-Science-Sandbox-Release

Version: 0.1.0

## Features

* #11: Created a notebook to show training with scikit-learn in the notebook
* #15: Installed exasol-notebook-connector via ansible
* #30: Added script to build the Data Science Sandbox as Docker Image
* #33: Added a notebook to securely manage sandbox configuration
* #30: Used the Secret Store in the Learning-in-the-notebook tutorial
* #41: Refactored the Transformer Extension notebook - made it use the Secret Store
* #53: Moved Jupyter notebooks to folder visible to ansible
* #16: Installed Jupyter notebooks via ansible
* #67: Removed apt cache to reduce image size
* #23: Fixed AWS Code build
* #69: Added entry point to start Jupyter server
* #84: Fixed retrieval and display of jupyter password
* #36: Supported pushing Docker image to a Docker registry

## Bug Fixes

* #1: Fixed CI build
* #61: Change initial password of Jupyter notebooks to "dss"

## Refactoring

* #5: Renamed all occurrences of "script language developer" by "data science"
* #56: Moved jupyter notebook files again
* #63: Improved logging of Ansible tasks
* #46: Enabled to suppress ansible output
* #52: Created CI build workflow to build and push Docker Image

## Documentation

* #58: Added location of Juypter notebooks to developer guide
