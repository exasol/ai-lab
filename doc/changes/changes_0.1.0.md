# ai-lab 0.1.0, released 2024-01-31

Code name: Initial release

## Summary

Initial release of the Exasol AI Lab. The project enables users to try out data science algorithms 
in Jupyter notebooks connected to the Exasol database. This release provides: 
- A JupyterLab environment with reference implementation notebooks of data science task using Exasol
- A Secure Configuration Store to easily and securely manage your credentials to a Exasol database and other external service
- The creation of an Amazon Machine Image (AMI), Virtual Machine Images, and a Docker Image for a specific version 
of the Exasol AI Lab project.

## AI-Lab-Release

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
* #115: Added VOLUME entry to Docker Image
* #78: Described persistent storage of notebook files and credential store
* #76: Added display of usage instructions for AI-Lab Docker edition
* #137: Set Jupyter lab default URL to AI-Lab start page
* #75: Changed default port of Jupyter server to 49494
* #79: Renamed data science sandbox to exasol-ai-lab
* #150: Used multipart upload for VM images
* #145: Added Docker Test Library to prepare Notebook tests
* #151: Setup SageMaker Credentials for notebook testing in the CI
* #155: Added a Notebook Link Checker to Github Actions
* #157: Added link checker for the documentation
* #136: Implemented notebook testing

## Bug Fixes

* #1: Fixed CI build
* #61: Change initial password of Jupyter notebooks to "dss"
* #161: Fixed the bug in the Transformers' Translation notebook.

## Refactoring

* #5: Renamed all occurrences of "script language developer" by "data science"
* #56: Moved jupyter notebook files again
* #63: Improved logging of Ansible tasks
* #46: Enabled to suppress ansible output
* #52: Created CI build workflow to build and push Docker Image
* #160: Implemented the PM's recommendations of 2024-01-24.

## Documentation

* #58: Added location of Juypter notebooks to developer guide
* #145: Split Development Guide
