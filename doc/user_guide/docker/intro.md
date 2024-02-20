# Need to Know About Docker Images and Containers

Exasol AI-Lab Docker Edition is published as a so-called _Docker Image_ on [Docker Hub](https://hub.docker.com/r/exasol/ai-lab).

In order to use such an image, you need two components
* Docker client
* Docker service, aka. _Docker daemon_

The client usually runs on your local machine, the daemon can be on the same machine, a remote machine, or inside a virtual machine.

The Docker client provides commands to download and manage such Docker Images.
Running a Docker Image results in a so-called _Docker Container_.
A Docker Container will maintain a _state_, including file system contents and running processes.
The client can be used to start, stop, and remove Docker Containers.

While a container is running you can
* Connect to IP ports exposed by the container
* Open a shell inside the container to interact with the container's file system or processes running inside the container, see command [`docker exec`](https://docs.docker.com/engine/reference/commandline/container_exec/)

When removing the container, all its processes are stopped and all changes to its file system are discarded. When you start a new container using the same image, then all changes will be lost and the file system contents will reset to default.

Please see [Managing User Data](managing-user-data.md) for preserving changes in the Jupyter notebook files and the [Secure Configuration Storage](secure-configuration-storage.md), though.



