# Using Exasol AI-Lab Docker Edition

Using Exasol AI-Lab Docker Edition requires some specific prerequisites but also offers additional benefits.

## Need to Know About Docker Images and Containers

Exasol AI-Lab Docker Edition is published as a so-called _Docker Image_ on [Docker Hub](https://hub.docker.com/r/exasol/data-science-sandbox).

In order to use such an image you need two components
* Docker client
* Docker service, aka. _Docker daemon_

The client must run on your local machine, the daemon can be on the same machine, a remote machine, or inside a virtual machine.

The Docker client provides commands to download and manage such Docker Images.
Running a Docker Image results in a so-called _Docker Container_.
A Docker Container will maintain a _state_, including file system contents and running processes.
The client can be used to start, stop, and remove Docker Containers.

While a container is running you can
* Connect to IP ports exposed by the container
* Open a shell inside the container to interact with the container's file system or processes running inside the container

When removing the container, all its processes are stopped and all changes to its file system are discarded. When you start a new container using the same image then all changes will be lost and the contents of its file system will be identical as defined by the image.

Please see [Managing User Data](managing_user_data.md) for preserving changes in the Jupyter notebook files and the [Secure Configuration Storage](secure_configuration_storage.md), though.

## Prerequisites

Before using Exasol AI-Lab Docker Edition you need to meet the following prerequisites:
* On the machine you want to interact with (e.g. localhost)
  * A Docker client installed
  * A free IP port to enable accessing the Jupyter server inside the Docker container
* The daemon machine must
  * Run a Linux operating system
  * Run a Docker daemon accessible from the Docker client
  * Have sufficient disk space to host the Docker image (size 1-2 GB) and run the Docker container

Please refer to the [Official Docker documentation](https://docs.docker.com) for installation and configuration.

## Operating Systems and Setups

Docker technology is available for a variety of operating systems and in multiple editions itself.

When your local machine runs on Linux operating system then there are no specific restrictions besides the general [hardware requirements](user_guide.md#hardware-requirements). In this case Exasol recommends to run the Docker daemon on the same machine to simplify the usage.

When your client is running on Windows or MacOSX then at least the daemon machine must run on Linux and some additional constraints and prerequisites need to be considered.

### Enabling Exasol AI-Lab to Use Docker Features

<!-- does this apply only to the docker edition? -->
<!-- for what does a user need these features? -->
<!-- How about the privileged mode required for Exasol Docker DB? -->

Exasol AI-Lab can use Docker features (DF) itself to provide additional convenience and features, such as starting an Exasol Docker-DB on demand.

<!-- How does the DinD relate to Linux operating system? -->

* If the Docker daemon runs on a virtual or remote machine different from your client machine then (HOW TO DO SO?).
* If your client machine is running on Windows or MacOSX then the following table lists additional constraints.

| Operating system | Setup           | Don't use DF | use DF |
|------------------|-----------------|--------------|--------|
| Windows          | Docker Desktop  | supported    | (1)    |
|                  | WSL 2           | supported    | (2)    |
|                  | Client Binaries | (1)          | (1)    |
| MacOSX           | Docker Desktop  | supported    | (2)    |
|                  | Client Binaries | (1)          | (1)    |

* (1) Requires a remote Docker daemon
* (2) Requires a remote Docker daemon or to mount `/var/run/docker.sock` into AI-Lab’s Docker container.

Please note that mounting the socket of a docker daemon running on your client machine into AI-Lab's Docker container creates security risks. In particular code running inside the AI-Lab could create privileged container and mount the filesystem of your host machine and gain root access to it.

So please check if this usage scenario is accepted by your organization. If not then either use a remote Docker daemon or do not enable AI-Lab to access the Docker daemon on your client machine.

### Recommendations and remote vs. local Docker daemon

* Exasol in general recommends to use Docker Desktop setup for Windows and MacOSX which implicitly uses a remote daemon in a managed machine.
* However, a daemon on remote machines or virtual machines can be used by all Docker clients.
* Docker volumes and port forwarding apply only for the remote system and you need to access the ports via the IP of the remote system.
  * An exception is https://docs.docker.com/desktop/networking/

## Defining Environment Variables

The Unix shell commands in the following sections will use some environment variables to make the commands portable and enable to adapt to your specific preferences while at the same time maintaining the ability to execute the commands verbatim without any change:
* Variable `VERSION` refers to the version of Exasol AI-Lab Docker Edition you want to use, alternativly you can use `latest`.
* Variable `PORT` refers to a free IP port on the machine running the Docker daemon
  * When running the Docker Container you must forward the port of the Jupyter service to this port in order to connect to it
* Variable `VOLUME` is expected to contain the name of your Docker volume.
* Variable `LISTEN_IP` defines the range of IP-addresses allowed to connect to the forwarded Jupyter port.
  * `0.0.0.0` means all IP-addresses are allowed.
  * For local setups, we recommend `127.0.0.1`.
  * Please contact your IT department if there are security restrictions.

Here are some sample values &mdash; please change to your needs:

```shell
VERSION=0.1.0
LISTEN_IP=0.0.0.0
PORT=8888
VOLUME=my-vol
```

## Starting a Docker Container from the Docker Image

The following command will
* Download the Docker image for the specified version `$VERSION` of the AI-Lab if not yet available in your Docker service
* Run a Docker container using this image
* Forward port `8888` to the specified `$PORT` on the daemon machine
  * allowing to connections from the IP-addresses listed in `$LISTEN_IP`

```shell
docker run \
  --detach \
  --volume ${VOLUME}:/root/notebooks \
  --publish ${LISTEN_IP}:${PORT}:8888 \
  exasol/data-science-sandbox:${VERSION}
```

### Enable AI-Lab to Access the Docker Daemon on the Client Machine

The following command assumes the Docker daemon to run on your client machine and mounts the daemon's socket into the AI-Lab Docker container.

```shell
docker run \
  --detach \
  --volume ${VOLUME}:/root/notebooks \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  --publish ${LISTEN_IP}:${PORT}:8888 \
  exasol/data-science-sandbox:${VERSION}
```

