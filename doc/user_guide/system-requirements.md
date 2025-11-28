# AI Lab System Requirements

The editions of the AI Lab have common requirements to be available on your system:
* CPU Architecture: x86_64 (64bit)
* CPU cores: minimum 1, recommended 2 cores
* Main memory (RAM): minimum 2 GiB, recommended 8 GiB
* Free disk space: minimum 2 GiB
* Network access
* Access to a running instance of an Exasol database
  * Alternatively you can start a small integrated Exasol Docker-DB.
    * When using AI Lab's Docker Edition there are [additional constraints](docker/prerequisites.md#enabling-exasol-ai-lab-to-use-docker-features).
  * **Please note**: AI Lab currently does not support Exasol SaaS.

When using the integrated Exasol Docker-DB then the machine needs to meet additional requirements:
* At least additional 2 GiB main memory (RAM)
* At least additional 15 GiB free disk space
