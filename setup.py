# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exasol_script_languages_container_ci_setup',
 'exasol_script_languages_container_ci_setup.cli',
 'exasol_script_languages_container_ci_setup.cli.commands',
 'exasol_script_languages_container_ci_setup.cli.options',
 'exasol_script_languages_container_ci_setup.lib']

package_data = \
{'': ['*'], 'exasol_script_languages_container_ci_setup': ['templates/*']}

install_requires = \
['PyGithub>=1.55.0,<2.0.0',
 'boto3>=1.22.0,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'exasol-script-languages-container-ci @ '
 'https://github.com/exasol/script-languages-container-ci/releases/download/0.3.0/exasol_script_languages_container_ci-0.3.0-py3-none-any.whl',
 'exasol_error_reporting_python @ '
 'git+https://github.com/exasol/error-reporting-python.git@0.2.0',
 'exasol_script_languages_container_tool @ '
 'https://github.com/exasol/script-languages-container-tool/releases/download/0.14.0/exasol_script_languages_container_tool-0.14.0-py3-none-any.whl',
 'jinja2>=3.1.0',
 'jsonschema>=3.2.0,<4.0.0']

setup_kwargs = {
    'name': 'exasol-script-languages-container-ci-setup',
    'version': '0.4.0',
    'description': 'Manages AWS cloud CI build infrastructure.',
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
