from collections import namedtuple


AnsibleRunContext = namedtuple("AnsibleRunContext", "playbook extra_vars")

default_ansible_run_context = AnsibleRunContext(playbook="slc_setup.yml", extra_vars=None)
