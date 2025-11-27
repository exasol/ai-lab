# Commands

The following command shows all commands provided by the AI Lab CLI:
```shell
poetry run ai-lab --help
```

The commands are organized in 3 groups:

| Group                | Usage                                   |
|----------------------|-----------------------------------------|
| Release Commands     | during the release                      |
| Deployment Commands  | to deploy infrastructure onto AWS cloud |
| Development Commands | to identify problems or for testing     |

## Release commands

The following commands are used during the release AWS Codebuild job:
* `create-vm`: Create a new AMI and VM images, see also [options for EC2 instances](#options-for-ec2-instances).
* `update-release`: Update release notes of an existing Github release.
* `start-release-build`: Start the release on AWS codebuild.
* `create-docker-image`: Create a Docker image for ai-lab and deploy it to hub.docker.com/exasol/ai-lab.

Script `start-release-build`:
* Is usually called from github workflow `release_droid_upload_github_release_assets.yml`.
* Requires environment variable `GH_TOKEN` to contain a valid token for access to Github.
* Requires to specify CLI option `--upload-url`.

This operation usually takes around than 1:40 hours.

## Developer commands

All other commands provide a subset of the features of the release commands, and can be used to identify problems or simulate the release:
* `export-vm`: Create a new VM image from a running EC2-Instance.
* `install-dependencies`: Start an ansible-installation onto an existing EC-2 instance.
* `reset-password`: Reset password on a remote EC-2-instance via ansible.
* `start-ec2`:
  * Start a new EC2 instance based on an Ubuntu AMI, see also [options for EC2 instances](#options-for-ec2-instances).
  * Option `--install-dependencies` additionally installs dependencies via Ansible.
  * The script will print the required SSH login for manual inspection or interaction with the EC2 instance.
  * The instance is kept running until the user presses Ctrl-C.
* `show-aws-assets`: Show AWS entities associated with a specific keyword (called __asset-id__).
* `start-test-release-build`: (For testing) Creates a release on Github and forwards it to the AWS Codebuild which creates VM images in various formats and attaches them to the Github release.
* `make-ami-public`: Change permissions of an existing AMI such that it becomes public.

Script `start-test-release-build` requires environment variable `GH_TOKEN` to contain a valid token for access to Github.

## Deployment commands

The following commands can be used to deploy the infrastructure onto a given AWS account:
* `setup-ci-codebuild`: Deploy the AWS Codebuild cloudformation stack which will run the ci-test.
* `setup-release-codebuild`: Deploy the AWS Codebuild cloudformation stack which will be used for the release-build.
* `setup-s3-bucket`: Deploy an AWS cloudformation stack with an S3 bucket, requires option `--purpose` (see below).
* `setup-waf`: Deploy an AWS cloudformation stack with a Web Application Firefall (WAF ACL) configuration for the Cloudfront distribution of an S3 bucket, requires option `--purpose` (see below).

Option `--purpose` is required for both commands `setup-s3-bucket` and `setup-s3-bucket-waf` to select the purpose of the s3 bucket. Supported values are
* `vm` for virtual machine images of the AI Lab
* `example-data-http` for example data to be used in the AI Lab and accessed via HTTP.
* `example-data-s3` for example data to be used via S3 protocol.

For all deployment commands:
* Don't forget to specify CLI option `--aws-profile`.
* Ensure the related AWS stack does not exist. If there was a rollback then please delete the stack manually, otherwise the script will fail.

If `setup-release-codebuild` or `setup-ci-codebuild` fails with error message "_Failed to create webhook. Repository not found or permission denied._" then
* Ensure to grant sufficient access permissions to the Github user used by the script.
* You can use a Github "_Repository role_" for that.
* The repository role must include the following permissions
  * Inherit the permissions from default role "Write"
  * Additional repository permission "Manage webhooks"
* In AWS you can configure the Github token by a resource with logical ID `CodeBuildCredentials`
  * Please note: There must be only one stack containing such a resource.
  * The definition of the AWS resource `CodeBuildCredentials` can use credentials from tha AWS secret manager.

```yaml
Resources:
  CodeBuildCredentials:
    Type: AWS::CodeBuild::SourceCredential
    Properties:
      ServerType: GITHUB
      AuthType: PERSONAL_ACCESS_TOKEN
      Username: "{{resolve:secretsmanager:github_personal_token:SecretString:github_user_name}}"
      Token: "{{resolve:secretsmanager:github_personal_token:SecretString:github_personal_token}}"
```

## Options for EC2 Instances

The commands `create-vm`, `start-ec2` are dealing with AWS EC2 instances and support additional options.

### Selecting an EC2 Instance Type

With option `--ec2-instance-type` you can specify the EC2 instance type.

Typical values for this CLI option are
* `t2.medium` -- the smallest and cheapest EC2 instance, this is the default.
* `g4dn.xlarge` -- an EC2 instance including a T4 GPU device for using GPU acceleration

### Selecting a Source AMI

With option `--ec2-source-ami` you can specify the source AMI (AWS Machine Image) to be used by the EC2 instance.

By default the `ai-lab` CLI commands will search for AMIs matching the pattern defined in file [lib/config.py](https://github.com/exasol/ai-lab/blob/main/exasol/ds/sandbox/lib/config.py).

You can find AMIs in the [AMI Catalog](https://eu-west-1.console.aws.amazon.com/ec2/home?region=eu-west-1#AMICatalog).

As the AI Lab currently only supports Python 3.10, you should select an AMI that has this version of Python installed, too. In particular Ubuntu 22.04 is recommended.

For GPU acceleration as of August 2025 the AI Lab proposes
* `--ec2-source-ami ami-006d6fd69373fa0fa`, which
  * is using a 64-bit x86 CPU
  * is labeled _Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04) 20250801_.
  * supports EC2 instances G4dn, G5, G6, Gr6, G6e, P4d, P4de, P5, P5e, P5en, P6-B200.
  * Requires `time_to_wait_for_polling: 60.0` seconds in file [config.py](https://github.com/exasol/ai-lab/blob/main/exasol/ds/sandbox/lib/config.py#L8).
  * Requires `Ebs: VolumeSize: 250` GB in file [ec2_cloudformation.jinja.yaml](https://github.com/exasol/ai-lab/blob/main/exasol/ds/sandbox/templates/ec2_cloudformation.jinja.yaml#L35).
* The 64-bit ARM variant is not supported by the DB
