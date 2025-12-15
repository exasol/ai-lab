## Maintaining the AI Lab Docker Edition

Developing the AI Lab Docker Edition may require changes to
* The entrypoint of the Docker image
* Startup options
* Environment variables

This document describes how to quickly change some details and inspect the effect.

### Creating a Custom Variant of the AI Lab Docker Image

For simple and quick experiments we recommend building a custom variant of the AI Lab Docker image:

* Create a local file `Dockerfile` containing
  ```
  FROM exasol/ai-lab:latest
  ```
* and run `docker build --tag xail-experiment`.

### Changing the Startup Options of the Entrypoint

If you want to change the startup options of the Entrypoint of the Docker image:

* Inspect the existing entrypoint definition of the AI Lab with shell command `docker inspect ai-lab:latest`
* Copy or modify the CLI options by adding a custom definition for `ENTRYPOINT` to your `Dockerfile`:
  ```
  FROM exasol/ai-lab:latest
  ENTRYPOINT ["sudo", "python3", "/home/jupyter/entrypoint.py", "--venv", "other-value" ]
  ```

### Change the Python Implementation of `entrypoint.py`

Finally you also can change the Python implementation of the entrypoint logic in file `entrypoint.py`:

* Create a local copy of file `exasol/ds/sandbox/runtime/ansible/roles/entrypoint/files/entrypoint.py`
* Add a `COPY` command to your `Dockerfile`
  ```
  FROM exasol/ai-lab:latest
  ENTRYPOINT ["sudo", "python3", "/home/jupyter/entrypoint.py", "--venv", "other-value" ]
  COPY entrypoint.py /home/jupyter/entrypoint.py
  ```
