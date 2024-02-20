# AI-Lab Docker Edition

Using Exasol AI-Lab Docker Edition requires some specific [prerequisites](prerequisites.md) but also offers additional benefits.

The [Operating System and Setup Guide](os-setup.md) helps you with the initial system setup.

AI-Lab also offers a [short introduction](intro.md) to Docker Images and Containers if you are new to this technology.

## Defining Environment Variables

The Unix shell commands in the following sections will use some environment variables. By this you can adapt the commands to your specific preferences while still being able to to execute them literally:
* Variable `VERSION` refers to the version of Exasol AI-Lab Docker Edition you want to use, alternativly you can use `latest`.
* Variable `VOLUME` is expected to contain the name of your Docker volume, see [Managing User Data](managing-user-data.md).
* Variable `LISTEN_IP` defines the range of IP-addresses allowed to connect to the forwarded Jupyter port.
  * `0.0.0.0` means all IP-addresses are allowed.
  * For local setups, we recommend `127.0.0.1`.
  * Please contact your IT department if there are security restrictions.

Here is an example:

```shell
VERSION=0.2.0
LISTEN_IP=0.0.0.0
VOLUME=my-vol
```

## Starting a Docker Container from the Docker Image

The following command will
* Download the Docker image for the specified version `$VERSION` of the AI-Lab if the image of the specified version is not yet available in your Docker service
* Run a Docker container using this image
* Mount the volume `$VOLUME` to the directory `/root/notebooks` inside the container
  * If the volume does not exist yet, then it will be created automatically.
* Forward port `49494` on the [daemon machine](prerequisites.md) to allow connections from all IP addresses matched by `$LISTEN_IP`

```shell
docker run \
  --volume ${VOLUME}:/root/notebooks \
  --publish ${LISTEN_IP}:49494:49494 \
  exasol/ai-lab:${VERSION}
```

Please note
* This is how you can start the AI-Lab if you are going to connect to an existing Exasol database.
* The [following section](#enable-ai-lab-to-access-the-docker-daemon) shows how to enable the AI-Lab to start an instance of Exasol Docker-DB.
* If you want to use a newer version of the AI-Lab then please delete Docker volumes created with older versions.

Additional options
* Add option `--detach` to run the container in the background but please note that the initial welcome message with instructions will be hidden then, see also command [`docker logs`](https://docs.docker.com/engine/reference/commandline/container_logs/).
* If port `49494` is not available on your daemon machine you can forward port `49494` of the Jupyter server in the Docker container to another port, e.g. `55555`, on the daemon machine with `--publish ${LISTEN_IP}:55555:49494`

### Enable AI-Lab to Access the Docker Daemon

The following command will enable AI-Lab to start an instance of Exasol Docker-DB, however
* Additional [Limitations and security risks](os-setup.md#enabling-exasol-ai-lab-to-use-docker-features) apply.
* Only file system objects on the daemon machine can be mounted. This applies to ordinary directories as well as the `docker.sock`.
* On Windows mounting `docker.sock` only works with Docker Desktop with WSL 2.
```shell
docker run \
  --volume ${VOLUME}:/root/notebooks \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  --publish ${LISTEN_IP}:49494:49494 \
  exasol/ai-lab:${VERSION}
```

## Connecting to Jupyter Service

When starting AI-Lab as Docker container the command line will display a welcome message showing connection instructions and a reminder to change the default password:

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

For parameter `<host>`: If your daemon machine is identical to the machine your browser is running on then you can replace `<host>` by `localhost` otherwise please use the IP address of the daemon machine.

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
docker exec --user root -it ${CONTAINER_ID} bash
```

## Installing Additional Dependencies

See [User Guide](../jupyter.md#installing-additional-dependencies).

Please note: Removing the docker container `docker rm <container>` will discard all dependencies that have been installed additionally.
