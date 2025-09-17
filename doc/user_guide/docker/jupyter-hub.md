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

[Jupyter Project](https://jupyter.org/) is inherently provides single-user environment. 
Both Jupyter Notebooks and more recent Jupyter Lab are using credentials and environment of the 
user who started the process, without addressing the scenarios when several users have to share
some resources provided by system administrators.

To mitigate this scenario, [JupyterHub](https://jupyter.org/hub) was created. On the high level,
it provides the web server which provides the following functionality:

* Authentication of users against pre-configured methods (PAM, OAuth, Kerberos, etc)
* Allocating required resources (starting virtual machines, for example)
* Spawning Jupyter processes for the user's needs.
* Traffic management between the user and Jupyter processes.

Together it provides convenient and flexible open-source tool, which allows administrators to build 
portals for corporate Jupyter users (Data Science teams, for example) or online courses (MOOCs).

More detailed description of JupyterHub architecture could be found in 
[A Conceptual Overview of JupyterHub](https://jupyterhub.readthedocs.io/en/stable/explanation/concepts.html) 
document.

## Custom image of ai-lab

With installed jupyter hub package

## JupyterHub configuration

## Minimalistic example

## Limitations 
