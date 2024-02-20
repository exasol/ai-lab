# AI-Lab Docker Edition

Using Exasol AI-Lab Docker Edition requires some specific [prerequisites](prerequisites.md) but also offers additional benefits.

The [Operating System and Setup Guide](prerequisites.md#operating-systems-and-setups) helps you with the initial system setup.

AI-Lab also offers a [short introduction](intro.md) to Docker Images and Containers if you are new to this technology.

## Defining Environment Variables

The Unix shell commands in the following sections will use some environment variables. By this you can adapt the commands to your specific preferences while still being able to execute them literally:
* Variable `VERSION` refers to the version of Exasol AI-Lab Docker Edition you want to use, alternatively you can use `latest`.
* Variable `VOLUME` is expected to contain the name of your Docker volume, see [Managing User Data](managing-user-data.md).
* Variable `LISTEN_IP` defines the range of IP-addresses allowed to connect to the forwarded Jupyter port.
  * `0.0.0.0` means all IP-addresses are allowed.
  * For local setups, we recommend `127.0.0.1`.
  * Please contact your IT department if there are security restrictions.
* Variable `CONTAINER_NAME` defines the name for the AI-Lab Docker container. Giving the running container a name makes it easier to refer to it when [stopping](#stopping-the-ai-lab-docker-container) or [restarting](#restarting-a-stopped-container) it.

Here is an example:

```shell
VERSION=0.2.0
LISTEN_IP=0.0.0.0
VOLUME=my-vol
CONTAINER_NAME=ai-lab
```

## Creating a Docker Container for the AI- Lab from the AI-Lab Docker Image

You can use an Exasol database with AI-Lab in two ways
* [External Exasol database](#ai-lab-with-exclusively-external-exasol-database)
* Integrated [Exasol Docker-DB](#ai-lab-with-integrated-exasol-docker-db) managed by AI-Lab

### AI-Lab with External Exasol Database Only

In this scenario the AI-Lab Docker container does not need access to the Docker daemon.

The following command will
* Download the Docker image for the specified version `$VERSION` of the AI-Lab if the image of the specified version is not yet available in your Docker service
* Run a Docker container using this image
* Mount the volume `$VOLUME` to the directory `/root/notebooks` inside the container
  * If the volume does not exist yet, then it will be created automatically.
* Forward port `49494` on the [daemon machine](prerequisites.md) to allow connections from all IP addresses matched by `$LISTEN_IP`

```shell
docker run \
  --name ${CONTAINER_NAME} \
  --volume ${VOLUME}:/root/notebooks \
  --publish ${LISTEN_IP}:49494:49494 \
  exasol/ai-lab:${VERSION}
```

If you want to use a newer version of the AI-Lab then please [delete the Docker volumes](managing-user-data.md#replacing-the-docker-volume) created with older versions.

Additional options
* Add option `--detach` to run the container in the background but please note that the initial welcome message with instructions will be hidden then, see also Command [`docker logs`](https://docs.docker.com/engine/reference/commandline/container_logs/) and section [Stopping the AI-Lab Docker Container](#stopping-the-ai-lab-docker-container).
* If port `49494` is not available on your daemon machine you can forward port `49494` of the Jupyter server in the Docker container to another port, e.g. `55555`, on the daemon machine with `--publish ${LISTEN_IP}:55555:49494`

### AI-Lab with integrated Exasol Docker-DB

In this scenario you must enable the AI-Lab Docker container to access the Docker daemon.

**Please note**
* Additional [Limitations and security risks](prerequisites.md#enabling-exasol-ai-lab-to-use-docker-features) apply.
* Only file system objects on the daemon machine can be mounted. This applies to ordinary directories as well as the `docker.sock`.
* On Windows mounting `docker.sock` only works with Docker Desktop with WSL 2.
```shell
docker run \
  --name ${CONTAINER_NAME} \
  --volume ${VOLUME}:/root/notebooks \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  --publish ${LISTEN_IP}:49494:49494 \
  exasol/ai-lab:${VERSION}
```

## Stopping the AI-Lab Docker Container

If you used one of the commands given in preceding sections without option `--detach` then you can stop the AI-Lab Docker container by simply pressing Ctrl-C.

If you used option `--detach` then you need to use the following command:

```shell
docker stop ${CONTAINER_NAME}
```

See also https://docs.docker.com/engine/reference/commandline/container_stop/.

## Restarting a Stopped Container

In general we recommend to restart a stopped container instead of creating a new one. This has the benefit of keeping [additional dependencies](#installing-additional-dependencies) that you did install:

```shell
docker start ${CONTAINER_NAME}
```

**Please note**
* If you accidently created a new AI-Lab Docker container and the stopped container still exists please remove the new container and restart the existing one.
* If there is no stopped AI-Lab container and you are using Exasol Docker-DB you need to link the newly created container to the Exasol Docker-DB network `db_network_DemoDb`.

```shell
docker network connect db_network_DemoDb <CONTAINER>
```

See also https://docs.docker.com/engine/reference/commandline/network_connect/.

## Connecting to the Jupyter Service

When starting AI-Lab as a Docker container the command line will display a welcome message showing connection instructions and a reminder to change the default password:

```
$ docker run --publish 0.0.0.0:$PORT:49494 exasol/ai-lab:$VERSION
Server for Jupyter has been started successfully.

You can connect with http://<host>:<port>

If using a Docker daemon on your local machine and did forward the
port to the same port then you can connect with http://localhost:49494.

┬ ┬┌─┐┌┬┐┌─┐┌┬┐┌─┐  ┬ ┬┌─┐┬ ┬┬─┐   ┬┬ ┬┌─┐┬ ┬┌┬┐┌─┐┬─┐  ┌─┐┌─┐┌─┐┌─┐┬ ┬┌─┐┬─┐┌┬┐ ┬
│ │├─┘ ││├─┤ │ ├┤   └┬┘│ ││ │├┬┘   ││ │├─┘└┬┘ │ ├┤ ├┬┘  ├─┘├─┤└─┐└─┐││││ │├┬┘ ││ │
└─┘┴  ─┴┘┴ ┴ ┴ └─┘   ┴ └─┘└─┘┴└─  └┘└─┘┴   ┴  ┴ └─┘┴└─  ┴  ┴ ┴└─┘└─┘└┴┘└─┘┴└──┴┘ o

The default password is "ai-lab".
To update the password, log in to the Docker container as the user root and run
    /root/jupyterenv/bin/jupyter-lab server password
```

Using an internet browser you then can connect to the Jupyter server running in the Docker container in order to follow the tutorials presented by a set of Jupyter notebooks, see [Connecting to Jupyter Service](../jupyter.md#open-jupyter-in-your-browser).

For the parameter `<host>`: If your daemon machine is identical to the machine your browser is running on then you can replace `<host>` by `localhost` otherwise please use the IP address of the daemon machine.

The following section explains how to log in to the Docker container to change settings, such as the default password.

## Logging in to the Docker container

To update the password you must log in to the Docker container.

First, you need to find out the container's ID. The following command shows the list of currently running Docker containers.

```shell
docker ps
```

Here is a sample output

```
CONTAINER ID   IMAGE     COMMAND        NAMES
1199447716d4   image:2   "entrypoint"   funny_rabbit
```

The following command enables you to log in as the user `root` to the specified container:

```shell
docker exec --user root -it ${CONTAINER_NAME} bash
```

## Installing Additional Dependencies

See [User Guide](../jupyter.md#installing-additional-dependencies).

Please note: Removing the docker container `docker rm <container>` will discard all dependencies that have been installed additionally.
