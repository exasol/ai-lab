import dataclasses
from typing import Any, Dict, Optional


@dataclasses.dataclass(frozen=True)
class AnsibleRunContext:
    playbook: str
    extra_vars: Optional[Dict[str, Any]]


default_ansible_run_context = AnsibleRunContext(playbook="ec2_playbook.yml", extra_vars=None)
reset_password_ansible_run_context = AnsibleRunContext(playbook="reset_password.yml", extra_vars=None)
