# Managing Your Notebook Files

Exasol AI-Lab comes with a set of Jupyter Notebook Files with file extension `.ipynb` demonstrating AI applications on top of Exasol database.

The Docker Edition of Exasol AI-Lab gives you additional options to manage these notebook files.

By default AI-Lab will instantiate the files with a predefined content. The predefined content may change with each release of the AI-Lab.

This document describes how to
* Edit these files and keep your changes
* Reuse your version of these files in future sessions
* Backup your changes persistently into a file archive
* Restore your changes from a file archive


## Basics

In order to save your changes persistently, to reuse, backup, and restore them, you need to create a so-called [_Docker Volume_](https://docs.docker.com/storage/volumes). The following sections describe how to
* Create a Docker volume
* Use the Docker volume in AI-Lab
* Remove the Docker volume
* Create a file backup of the contents of the Docker volume
* Restore the contents of the Docker volume from a backup

When running the AI-Lab in a Docker container then AI-Lab keeps the notebook files in directory `/root/notebooks` inside the Docker container.

## Additional Environment Variables

Folowing the general [User Guide for the Exasol AI-Lab Docker Edition](ai_lab_docker_edition.md#defining-environment-variables) this document uses some additional environment variables:
* Variable `VOLUME` is expected to contain the name of your Docker volume.
* Variable `DIR` is expected to point to a directory to contain your backup.

Here are some sample values &mdash; please change to your needs:

```shell
VOLUME=my-vol
DIR=~/tmp/backup
```

## Creating a Volume

The following command creates an empty Docker volume with the name specified by environment variable `$VOLUME`.

```shell
docker volume create $VOLUME
```

## Using Your Volume in the AI-Lab Docker Container

See also [Restore volume from a backup](https://docs.docker.com/storage/volumes/#restore-volume-from-a-backup) in official Docker documentation.

The following shell command runs AI-Lab as a Docker container while mounting your volume to folder `/root/notebooks`.

```shell
docker run \
  --detach \
  --publish 0.0.0.0:$PORT:8888 \
  --volume $VOLUME:/root/notebooks \
  exasol/data-science-sandbox:$VERSION
```

## Removing Your Volume

If you don't need the contents of your Docker volume anymore then the following command removes your Docker volume:

```shell
docker volume rm $VOLUME
```

## Creating a Backup of Your Volume

See also [Back up a volume](https://docs.docker.com/storage/volumes/#back-up-a-volume) in official Docker documentation.

The following shell commands
* Run a Docker command to backup the volume
  * Option `-rm` removes the container after exit.
  * The `--volume` options mount your volume and your backup directory to enable the Docker container to access them.
* The `tar` command executed inside the Docker container uses
  * Option `-C` to change to directory `/volume`
  * Option `-c` to create a file archive
  * Option `-z` to apply gzip compressions in order to reduce the file size
  * Option `-v` to be verbose and display the progress of the operation
  * Option `-f` to specify the path of the file archive
* call `tar` to display the contents of the backup in file `$DIR/backup.tar` using
  * Option `-t` to list the archive contents
  * Option `-f` to specify the path of the file archive to list

```shell
docker run --rm \
  --volume $VOLUME:/volume \
  --volume $DIR:/dest \
  ubuntu \
  tar -C /volume -czvf /dest/backup.tgz .
tar tf $DIR/backup.tgz
```

<!-- -------------------------------------------------- -->
## Restoring Your Volume From a Backup

See also [Restore volume from a backup](https://docs.docker.com/storage/volumes/#restore-volume-from-a-backup) in official Docker documentation.

The following shell command runs a Docker command to restore a volume's content from a backup:

```shell
docker run --rm \
  --volume $VOLUME:/volume \
  --volume $DIR:/dest \
  ubuntu \
  tar -C /volume -xvf /dest/backup.tgz
```

The `tar` command executed inside the Docker container uses
  * Option `-C` to change to directory `/volume`
  * Option `-x` to extract the file archive
  * Option `-v` to be verbose and display the progress of the operation
  * Option `-f` to specify the path of the file archive
