# Exasol AI Lab

The Exasol AI Lab is a pre-configured container designed to empower data scientists to build AI & ML workflows on top of their Exasol database. It streamlines common data science and AI tasks, including data loading, preparation, exploration, model training, and deployment. Whether you’re a seasoned practitioner or just getting started, AI Lab is your one-stop-shop for AI and machine learning on Exasol.

Key Features:
* **Jupyter Notebook Environment**: The heart of the AI Lab is a robust Jupyter Notebook environment. It is where you will work on your AI and Data Science projects.
* **Exasol Integration**: Leverage Exasol’s power for your AI and machine learning use cases. The AI Lab includes essential Exasol packages, extensions, and configuration tasks.
* **Example Notebooks**: Jumpstart your work with ready-to-use example notebooks. Explore classic machine learning scenarios (think scikit-learn), seamlessly integrate Exasol with AWS SageMaker, and tap into Hugging Face models directly within Exasol.
* **Generative AI Support**: AI Lab is equipped with tools and libraries to help you explore generative AI techniques, including transformer models and large language models (LLMs).
* **Traditional ML and Data Science**: AI Lab supports traditional machine learning and data science workflows, making it a versatile tool for various projects.

## Getting Started

The fastest way to get started with AI Lab is to use its [Docker Edition](doc/user_guide/docker/docker-usage.md) via [Docker](https://www.docker.com/).

### Install AI Lab via Docker

Once you have Docker installed, you can pull the latest AI Lab image from Docker Hub and run it as a container using the following commands:

```shell
VERSION=latest
LISTEN_IP=0.0.0.0
VOLUME=my-vol
CONTAINER_NAME=ai-lab
````

```shell
docker run \
  --name ${CONTAINER_NAME} \
  --volume ${VOLUME}:/home/jupyter/notebooks \
  --publish ${LISTEN_IP}:49494:49494 \
  exasol/ai-lab:${VERSION}
```

### Access the Web Interface

You can now access AI Lab's web interface by navigating to `http://localhost:49494` in your web browser. If necessary, replace `<host>` with the IP address or hostname of the machine where the Docker container is running.

You will be asked to enter a password. The default password is `ailab`. The User Guide provides instructions on how to [change the default password](doc/user_guide/docker/docker-usage.md#connecting-to-the-jupyter-service).

### Configure AI Lab to Connect to Your Exasol Database

You can use AI Lab with an existing Exasol database OR you can use AI Lab to spin up a standalone Exasol database in another Docker container.

Once you have opened your browser, navigated to the AI Lab interface and logged in, open the `main_config.ipynb` notebook and follow all of the steps to configure a connection to Exasol.

### Run your first Workflow

Now that you have AI Lab up and running, you can start exploring the various notebooks and tutorials! We recommend starting with the `first_steps.ipynb` notebook, which provides a brief introduction to using AI Lab.

## Next Steps

AI Lab offers a comprehensive set of features as well as alternative deployment options. When you are ready to dive deeper, check out the **[User Guide](doc/user_guide/user-guide.md)** for more detailed instructions.