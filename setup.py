# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exasol_script_languages_developer_sandbox',
 'exasol_script_languages_developer_sandbox.cli',
 'exasol_script_languages_developer_sandbox.cli.commands',
 'exasol_script_languages_developer_sandbox.cli.options',
 'exasol_script_languages_developer_sandbox.lib',
 'exasol_script_languages_developer_sandbox.lib.ansible',
 'exasol_script_languages_developer_sandbox.lib.asset_printing',
 'exasol_script_languages_developer_sandbox.lib.aws_access',
 'exasol_script_languages_developer_sandbox.lib.ci_codebuild',
 'exasol_script_languages_developer_sandbox.lib.export_vm',
 'exasol_script_languages_developer_sandbox.lib.setup_ec2',
 'exasol_script_languages_developer_sandbox.lib.vm_bucket',
 'exasol_script_languages_developer_sandbox.runtime']

package_data = \
{'': ['*'],
 'exasol_script_languages_developer_sandbox': ['templates/*'],
 'exasol_script_languages_developer_sandbox.runtime': ['ansible/*',
                                                       'ansible/roles/docker/defaults/*',
                                                       'ansible/roles/docker/tasks/*',
                                                       'ansible/roles/jupyter/defaults/*',
                                                       'ansible/roles/jupyter/files/*',
                                                       'ansible/roles/jupyter/tasks/*',
                                                       'ansible/roles/jupyter/templates/etc/systemd/system/*',
                                                       'ansible/roles/poetry/defaults/*',
                                                       'ansible/roles/poetry/tasks/*',
                                                       'ansible/roles/script_languages/defaults/*',
                                                       'ansible/roles/script_languages/tasks/*']}

install_requires = \
['ansible-runner>=2.2.1,<3.0.0',
 'ansible>=6.1.0,<7.0.0',
 'boto3>=1.22.0,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'exasol_script_languages_release @ '
 'git+https://github.com/exasol/script-languages-release.git@develop',
 'importlib_resources>=5.4.0',
 'jinja2>=3.1.0',
 'pandas>=1.4.0,<2.0.0',
 'rich>=12.5.1,<13.0.0']

setup_kwargs = {
    'name': 'exasol-script-languages-developer-sandbox',
    'version': '0.1.0',
    'description': 'Manages script-languages developer virtual machines.',
    'long_description': None,
    'author': 'Thomas Uebensee',
    'author_email': 'ext.thomas.uebensee@exasol.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<4.0',
}


setup(**setup_kwargs)
