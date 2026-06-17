# Notebook Deployment

AI Lab notebooks are deployed from the Notebook Connector package during image builds.
The Docker image build runs the Notebook Connector CLI command `ai-lab deploy-notebooks`
to populate the initial notebook directory used by Jupyter.

## Notebook Connector

The `exasol-notebook-connector` package provides the notebook helper functions and the
packaged notebooks that AI Lab ships in its images.
Its dependencies are still listed in
[notebook_requirements.txt](../../exasol/ds/sandbox/runtime/ansible/roles/jupyter/files/notebook_requirements.txt)
and are installed into the Jupyter virtual environment during the build.

When you need to update notebooks, change them in the Notebook Connector project and
rebuild the AI Lab image. This repository no longer carries a separate notebook source tree.

## Notebook Testing

We run notebook tests in the Docker edition of AI Lab by building a test image on top of
the AI Lab Docker image and installing the test dependencies from
[test/notebooks](../../test/notebooks).
Notebook test names need to fit the pattern `nbtest_*.py`, so pytest does not run them
outside the notebook test runner.

Environment variables with the prefix `NBTEST_` are forwarded into the Docker container and
to the notebook test. You can use this to forward secrets to the notebook tests.

By default all created containers and images are removed after running the tests regardless
of success or failure.
However, with the following pytest command line parameters you can keep them or reuse them
to speed up local testing:

```text
  --dss-docker-image=DSS_DOCKER_IMAGE
                        Name and version of existing Docker image to use for tests
  --keep-dss-docker-image
                        Keep the created dss docker image for inspection or reuse.
  --docker-image-notebook-test=DOCKER_IMAGE_NOTEBOOK_TEST
                        Name and version of existing Docker image for Notebook testing to use for tests
  --keep-docker-image-notebook-test
                        Keep the created notebook-test docker image for inspection or reuse.
```
