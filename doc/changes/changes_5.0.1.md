# AI-Lab 5.0.1 released 2026-05-13

Code name: Release Flow Migration

## Summary

This release moves the AI-Lab release flow from release-specific AWS CodeBuild to a tag-triggered GitHub Actions workflow.
GitHub Actions now authenticates to AWS via OIDC and still builds the AMI, VM, and Docker release artifacts.

## Features


## Documentation


## Refactorings

* #515: Moved AI-Lab release CodeBuild from AWS to GitHub
