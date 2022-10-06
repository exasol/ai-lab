# script-languages-developer-sandbox 0.1.0, released 2022-10-06

Code name: Initial release

## Summary

Initial release of the script-languages-developer-sandbox. It provides the creation of a developer sandbox AMI and virtual machine images for a specific version of the script-languages-release project.

## Script-Languages-Release

Version: 5.0.0

## Bug Fixes
 
 - #18: Fixed network connection 
 - #51: Fixed network connection
 - #57: Fixed release build

## Features / Enhancements

 - #2: Implemented launch of an EC2 instance
 - #3: Installed SLC dependencies via Ansible
 - #4: Implemented deployment and access of S3 Bucket for VM's
 - #5: Implemented export of VM's
 - #24: Move CI test to AWS Codebuild
 - #25: Implemented motd message about Jupyter password change
 - #8: Implemented a release workflow
 - #36: Added make-ami-public option
 - #43: Added CDN to the S3 VM Bucket
 - #45: Protected cloudfront access
 - #47: Renamed virtual images 
 - #38: Included tutorial Jupyterlab notebook

## Documentation

 - #19: Added user guide and developer guide
 - #49: Added tutorial about how to start the VM/AMI

## Refactoring

 - #22: Improved logging
 - #26: Implemented search for latest AMI
 - #12: Updated the script-languages-release tag with the correct version
 - #21: Minor refactoring tasks
 - #41: Renamed cloudformation stack