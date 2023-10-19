import subprocess


def validate_using_cfn_lint(tmp_path, cloudformation_yml):
    """
    This test uses cfn-lint to validate the Cloudformation template.
    (See https://github.com/aws-cloudformation/cfn-lint)
    """
    out_file = tmp_path / "cloudformation.yaml"
    with open(out_file, "w") as f:
        f.write(cloudformation_yml)

    completed_process = subprocess.run(["cfn-lint", str(out_file.absolute())], capture_output=True)
    try:
        completed_process.check_returncode()
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        raise e

