# Notebook Files

AI-Lab repository includes some Jupyter notebooks and scripts to add these notebooks to AI-Lab images (the old name - DSS images), e.g. AMI or Docker Images.

Please add or update the notebook files in folder [exasol/ds/sandbox/runtime/ansible/roles/jupyter/files/notebook](../../exasol/ds/sandbox/runtime/ansible/roles/jupyter/files/notebook).

## Notebook Connector

Most notebooks use the `exasol-notebook-connector` - the component providing various helper functions for notebooks.
We typically put there the code we don't want to show in a notebook. Logically, this component is a part of the AI-Lab.
It is listed in the [notebook_requirements.txt](../../exasol/ds/sandbox/runtime/ansible/roles/jupyter/files/notebook_requirements.txt) and gets installed in the container with pip.
In order to simplify making simultaneous changes to both notebooks and the notebook-connector we allow referencing the latter temporarily through a git dependency,
e.g. `exasol-notebook-connector @ git+https://github.com/exasol/notebook-connector@e3a8525`.
It is important to reference a commit in the `main` branch, not the `main` branch itself. The git dependency should be
replaced with the proper pypi dependency before releasing of the AI-Lab.

## Work-in-progress Notebooks

Sometimes, we might have notebooks which we don't want to release yet, either because they are incomplete or 
only a pre-release. However, we already want to test these notebooks using the notebook tests or build 
Docker images that contain them.
These work-in-progress notebooks should be located in the following directory:

```exasol/ds/sandbox/runtime/ansible/roles/jupyter/files/notebook/work_in_progress```

The directory then only gets copied into the Docker image when either the test parameter `work_in_progress_notebooks`
is requesting it or if you use the commandline option `--work-in-progress-notebooks` is added to the 
`create-docker-image` command in the CLI.

## Notebook Testing

We are running tests for the notebooks in the Docker Edition of the AI Lab. For this we are creating a Docker test setup in 
[test_notebooks_in_dss_docker_image.py](../../test/notebook_test_runner/test_notebooks_in_dss_docker_image.py) which installs test libraries into the AI Lab Docker Image.
It further creates a new test and Docker Container for each notebook test in [test/notebooks](../../test/notebooks). 
Notebook test names need to fit the pattern `nbtest_*.py`, to prevent pytest running them outside of Docker setup.

Environment variables with the prefix `NBTEST_` with which you call
[test_notebooks_in_dss_docker_image.py](../../test/notebook_test_runner/test_notebooks_in_dss_docker_image.py) are forwarded 
into the Docker container and to the notebook test. You can use this to forward secrets to the notebook tests.

By default all created containers and images are removed after running the tests regardless of success or failure.
However, with the following pytest commandline parameters you can keep them or reuse them to speed up local testing:

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