# Commands

The AI-Lab CLI offers commands in the following three groups:

| Group                | Usage                                   |
|----------------------|-----------------------------------------|
| Release Commands     | during the release                      |
| Deployment Commands  | to deploy infrastructure onto AWS cloud |
| Development Commands | to identify problems or for testing     |

## Release commands

The following commands are used during the release AWS Codebuild job:
* `create-vm`: Create a new AMI and VM images.
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
* `setup-ec2`: Start a new EC2 instance (based on an Ubuntu AMI).
* `setup-ec2-and-install-dependencies`: Start a new EC2 instance and install dependencies via Ansible.
  * The script will print the required SSH login for manual inspection or interaction with the EC2 instance.
  * The instance is kept running until the user presses Ctrl-C.
* `show-aws-assets`: Show AWS entities associated with a specific keyword (called __asset-id__).
* `start-test-release-build`: (For testing) Creates a release on Github and forwards it to the AWS Codebuild which creates VM images in various formats and attaches them to the Github release.
* `make-ami-public`: Change permissions of an existing AMI such that it becomes public.

Script `start-test-release-build` requires environment variable `GH_TOKEN` to contain a valid token for access to Github.

## Deployment commands

The following commands can be used to deploy the infrastructure onto a given AWS account:
* `setup-ci-codebuild`: Deploy the AWS Codebuild cloudformation stack which will run the ci-test.
* `setup-vm-bucket`: Deploy the AWS Bucket cloudformation stack which will be used to deploy the VM images.
* `setup-release-codebuild`: Deploy the AWS Codebuild cloudformation stack which will be used for the release-build.
* `setup-vm-bucket-waf`: Deploy the AWS Codebuild cloudformation stack which contains the WAF Acl configuration for the Cloudfront distribution of the VM Bucket.

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