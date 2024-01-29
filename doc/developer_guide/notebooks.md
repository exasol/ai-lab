# Notebook Files

DSS repository includes some Jupyter notebooks and scripts to add these notebooks to DSS images, e.g. AMI or Docker Images.

Please add or update the notebook files in folder [exasol/ds/sandbox/runtime/ansible/roles/jupyter/files/notebook](../../exasol/ds/sandbox/runtime/ansible/roles/jupyter/files/notebook).

## Notebook Testing

We are running tests for the notebooks in the Docker Edition of the AI Lab. For this we are creating a Docker test setup in 
[test_notebooks_in_dss_docker_image.py](test/integration/test_notebooks_in_dss_docker_image.py) which installs test libraries into the AI Lab Docker Image.
It further creates a new test and Docker Container for each notebook test in [test/notebooks](test/notebooks). 
Notebook test names need to fit the pattern `nbtest_*.py`, to prevent pytest running them outside of Docker setup.

Environment variables with the prefix `NBTEST_` with which you call
[test_notebooks_in_dss_docker_image.py](test/integration/test_notebooks_in_dss_docker_image.py) are forwarded 
into the Docker container and to the notebook test. You can use this to forward secrets to the notebook tests.

Per default all created containers and images are removed after running the tests regardless of success or failure.
However, with the following pytest commandline parameters you can keep them or reuse them for speed up local testing:

```
  --dss-docker-image=DSS_DOCKER_IMAGE
                        Name and version of existing Docker image to use for tests
  --keep-dss-docker-image
                        Keep the created dss docker image for inspection or reuse.
  --docker-image-notebook-test=DOCKER_IMAGE_NOTEBOOK_TEST
                        Name and version of existing Docker image for Notebook testing to use for tests
  --keep-docker-image-notebook-test
                        Keep the created notebook-test docker image for inspection or reuse.
```