# Using Exasol AI-Lab Docker Edition

Using Exasol AI-Lab Docker Edition requires some specific prerequisites but also offers some additional benefits.

## Need to Know About Docker Images and Containers

Exasol AI-Lab Docker Edition is published as a so-called _Docker Image_ on [Docker Hub](https://hub.docker.com/r/exasol/data-science-sandbox).

The Docker client provides commands to download and manage such Docker Images.
When running a Docker Image results in a so-called _Docker Container_.
A Docker Container will maintain a _state_ including file system contents and running processes.
A Docker Container can be started, stopped, and removed.

While running you can
* Connect to IP ports exposed by the Docker Container
* Open a shell inside the Docker Container to interact with the file system or running processes

When removing the container, all processes are stopped and all changes to the file system are discarded.
When you start a new container using the same image then the contents of its file system will be identical as defined by the image and all changes will be lost.

Please see [Managing User Data](user_data.md) for preserving changes in the Jupyter notebook files and the [Secure Configuration Storage](secure_configuration_storage.md), though.

## Prerequisites

Before using Exasol AI-Lab Docker Edition you need to meet the following prerequisites:
* On the machine you want to interact with (e.g. localhost)
  * A Docker client installed
  * A free IP port to enable accessing the Jupyter server inside the Docker container
* On the same or a different machine
  * A Docker daemon or Docker service accessible from the Docker client
  * Enough disk space to host the Docker Image (size 1-2 GB) and run the Docker container

Please refer to the [Official Docker documentation](https://docs.docker.com) for installation and configuration.

## Defining Environment Variables

The Unix shell commands in the following sections will use some environment variables to make the commands portable and enable to adapt to your specific preferences while at the same time maintaining the ability to execute the commands verbatim without any change:
* Variable `VERSION` refers to the version of Exasol AI-Lab Docker Edition you want to use, alternativly you can use `latest`.
* Variable `PORT` refers to a free IP port on the machine running the Docker daemon
  * When running the Docker Container you must forward the port of the Jupyter service to this port in order to connect to it

Here are some sample values &mdash; please change to your needs:

```shell
VERSION=0.1.0
PORT=8888
```

## Starting a Docker Container from the Docker Image

The following command will
* Download the Docker image for the specified version `$VERSION` of the AI-Lab if not yet available in your Docker service
* Run a Docker container using this image
* Forward port `8888` to the specified `$PORT` on the machine running the Docker service, e.g. your local host


```shell
docker run \
  --detach \
  --publish 0.0.0.0:$PORT:8888 \
  exasol/data-science-sandbox:$VERSION
```

## Managing Jupyter Notebook Files

Exasol AI-Lab Docker Edition gives you additional options to manage these notebook files, see [Managing User Data](user_data.md).