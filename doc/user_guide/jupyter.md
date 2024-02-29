## Open Jupyter In Your Browser

| Item                | Location or value                         |
|---------------------|-------------------------------------------|
| Virtual environment | location `/home/jupyter/jupyterenv`       |
| Location notebooks  | location `/home/jupyter/notebooks`        |
| Password            | `ailab`                                   |
| HTTP Port           | `49494` (or the port you forwarded it to) |

Exasol strongly recommends changing the Jupyter password as soon as possible. Details about how to do that will be shown in the login screen.

Check [Jupyter Home](https://jupyter.org/) for more information.

You can open the starting page with `https://<host>:<port>`.

Please note specific instructions for [AI-Lab Docker Edition](docker/docker-usage.md).

## Installing Additional Dependencies

Using one of the Jupyter notebooks you can simply add a cell and execute [magic-pip](https://ipython.readthedocs.io/en/stable/interactive/magics.html#magic-pip) in it.

The following command installs Python dependency `stream-zip`:
```shell
%pip install --upgrade stream-zip
```

Please note the limited lifetime of additional dependencies for [AI-Lab Docker Edition](docker/docker-usage.md#installing-additional-dependencies).
