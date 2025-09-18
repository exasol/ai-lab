# AI Lab in a JupyterHub Environment

[JupyterHub](https://jupyter.org/hub) is a popular way to manage multi-user access 
to Jupyter environments. If your organization is using or planing to use JupyterHub to 
provide different groups of users access to the preconfigured Jupyter environments, you might 
find this document relevant.

This is not a complete detailed manual about JupyterHub setup and configuration - this topic is broad
and well beyond the scope of this document. In addition, support of JupyterHub in AI Lab is 
very experimental and you might encounter some issues and limitations. This document is rather 
a draft, describing how the AI Lab docker container can be integrate into the JupyterHub environment. 
Where needed, we provide links to the JupyterHub documentation for further reading.
If you face some problems, don't hesitate to file a [bug report](https://github.com/exasol/ai-lab/issues).

## Introduction

[Jupyter Project](https://jupyter.org/) inherently provides a single-user environment. 
Both Jupyter Notebook and the more recent Jupyter Lab use the credentials and environment of the 
user who started the process, without addressing scenarios in which multiple users must share 
resources provided by system administrators.

To mitigate this scenario, [JupyterHub](https://jupyter.org/hub) was created. At a high level,
it provides a web server that offers the following functionality:

* Authentication of users against preconfigured methods (PAM, OAuth, Kerberos, etc.)
* Allocation required resources (for example, starting virtual machines)
* Spawning Jupyter processes for users.
* Managing traffic between users and Jupyter processes.

Together they provide a convenient and flexible open-source tool, which allows administrators to build 
portals for corporate Jupyter users (for example, Data Science teams) or online courses (MOOCs).

A more detailed description of the JupyterHub architecture can be found in 
[A Conceptual Overview of JupyterHub](https://jupyterhub.readthedocs.io/en/stable/explanation/concepts.html) 
document.

## Custom image of ai-lab

With installed jupyter hub package

## JupyterHub configuration

## Minimalistic example

## Limitations 
