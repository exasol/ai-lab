## Prerequisites for Using AI-Lab Docker Edition

Before using Exasol AI-Lab Docker Edition you need to meet the following prerequisites:
* On the machine you want to interact with (e.g. localhost)
  * A Docker client must be installed
* The daemon machine must
  * Run a Linux operating system
  * Run a Docker daemon accessible from the Docker client
  * Meet the [system requirements](../system-requirements.md)
  * Have a free IP port to enable accessing the Jupyter server inside the Docker container
    * When using Docker Desktop, it will forward the port to its internal VM _and_ to your client machine as well. In this case the IP port must be free on both systems, see also https://docs.docker.com/desktop/networking/.

![Image](docker.png)

Please refer to the [Official Docker documentation](https://docs.docker.com) for installation and configuration.

Docker volumes and port forwarding apply only for the daemon machine, and you need to access the ports via the IP of the daemon machine. An exception is described in https://docs.docker.com/desktop/networking/.

## Operating Systems and Setups

Docker technology is available for a variety of operating systems. On some platforms, there are multiple editions of it.

When your local machine runs on Linux operating system then there are no specific restrictions besides the general [system requirements](../system-requirements.md). In this case Exasol recommends running the Docker daemon on the same machine to simplify the usage.

When your client is running on Windows or MacOSX then at least the daemon machine must run on Linux. Docker Desktop usually includes a Linux VM with the Docker daemon.

See the next section for a list of verified setups.

### Enabling Exasol AI-Lab to Use Docker Features

<!-- later on AI-Lab will be enhanced to create SLCs, as well. -->
Exasol AI-Lab can use Docker features to provide additional convenience and features, such as starting an Exasol Docker-DB on demand.

<!-- Client Binaries are omitted on purpose, possible on Linux -->
This is only possible when using
* Linux
* Windows Docker Desktop with WSL 2
* Windows Docker Desktop with a remote Docker daemon
* MacOSX Docker Desktop
* MacOSX Docker Desktop with a remote Docker daemon

In all scenarios the daemon machine must allow running the Exasol Docker-DB with option [`--privileged`](https://docs.docker.com/engine/reference/run/#runtime-privilege-and-linux-capabilities).

Please note that enabling Exasol AI-Lab to use Docker features creates security risks. In particular, code running inside the AI-Lab could create privileged containers, mount the file system of the machine running the Docker daemon, and gain root access to it. For details see https://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci/, section "The socket solution".

Section [AI-Lab Managing Exasol Docker-DB Internally](docker-usage.md#ai-lab-with-integrated-exasol-docker-db) shows the corresponding command line options, for details see [Docker FAQ](https://docs.docker.com/desktop/faqs/general/#how-do-i-connect-to-the-remote-docker-engine-api).
