# AI-Lab System Requirements

The editions of the AI-Lab have common requirements to be available on your system:
* CPU Architecture: x86
* CPU cores: minimum 1, recommended 2 cores
* Main memory (RAM): minimum 2 GiB, recommended 8 GiB
* Network access
* Recommend access to a running instance of Exasol database, otherwise you can start a small Exasol Docker-DB
  * Please note: AI-Lab currently does not support Exasol SaaS.

As the AI-Lab is meant to explore AI applications on top of the Exasol database, you need an instance of the Exasol database running and be able to connect to it.

All editions of AI-Lab can automatically launch such an instance on demand. However, when using AI-Lab's Docker Edition there are [additional constraints](docker/prerequisites.md#enabling-exasol-ai-lab-to-use-docker-features).

When running Exasol database in a Docker container then the machine needs to meet [additional requirements](https://github.com/exasol/integration-test-docker-environment/blob/main/doc/user_guide/user_guide.rst).