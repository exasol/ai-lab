## Design Goals

The Exasol AI-Lab (XAIL) uses AWS as backend, because it provides the possibility to run the whole workflow during a ci-test.

This project uses

* `boto3` to interact with AWS
* `pygithub` to interact with the Github releases
* `ansible-runner` to interact with Ansible.
  Proxy classes to those projects are injected at the CLI layer. This allows to inject mock classes in the unit tests.
  A CLI command has normally a respective function in the `lib` submodule. Hence, the CLI layer should not contain any
  logic, but invoke the respective library function only. Also, the proxy classes which abstract the dependant packages
  shall not contain too much logic. Ideally they should invoke only one function to the respective package.
