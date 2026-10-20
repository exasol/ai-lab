# AI-Lab 7.0.0 released 2026-10-20

Code name: AI-Function integration

## Summary

This release uses [exasol-notebook-connector 3.1.0](https://github.com/exasol/notebook-connector/releases/tag/3.1.0)
with Transformers-Extension 5.2.0. This update integrates the New AI-Function Notebook updates.
We also switched AI-lab ansible images to Ubuntu 24.04/Python 3.12.

## Changes

* #547: Added Exasol Toolbox support for selected Nox sessions.
* #547: Updated the pinned Ubuntu `network-manager` package to restore AWS CI provisioning.
* #547: Updated transitive Python dependencies in `poetry.lock`.
* #551: Integrated new AI-Functions with exasol-notebook-connector version 3.1.0. 
* #551: Switched AI-lab ansible images to Ubuntu 24.04/Python 3.12.
