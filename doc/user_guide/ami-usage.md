# AI-Lab AMI Edition (Amazon Machine Image)

The ID of the AMI (Amazon Machine Image) is mentioned in the [release notes](https://github.com/exasol/ai-lab/releases/latest) and can be used to start an EC2-instance in your AWS account.

The naming scheme is: "_Exasol-AI-Lab-${VERSION}_", e.g. "_Exasol-AI-Lab-5.0.0_"

The AMI is currently only available in the AWS region `eu-central-1`.

Check the [AWS documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/CopyingAMIs.html) for details about how to copy the image.

## Overview

1. Create a Security Group with open inbound ports for `ssh` (22) and `Jupyter` (49494)
2. Start the EC-2 instance

## Step-by-step

1. Go to [AWS Console](https://aws.amazon.com/console/)
2. Go to EC2 (in the search field at the top type EC2 and click on the result)
3. Create a security group for ssh and (optionally) Jupyter:
    - In the navigation bar on the left select "Security Groups"
    - Click button "Create Security Group"
    - Choose name and VPC
    - For outbound rules keep the default
    - Create  inbound rules:
      - One of type `ssh`
      - If you plan to connect to the Jupyter lab, add another rule of type "Custom TCP" with port 49494.
        - **Important**: With this rule you expose the Jupyter lab to the internet; anybody who has access to the password will be able to execute commands. For a minimum of security you should change the default Jupyter password. Details about how to do that will be shown in the login screen when you login via ssh. However, you should consider to use only `ssh` with port forwarding.
 4. Go back to the EC2 console
 5. Launch the EC2 instance:
     - In the navigation bar on the left select "Instances"
     - Click button "Launch instances"
     - At field "Application and OS Images" select the AMI id of the sandbox (found in the [release notes](https://github.com/exasol/ai-lab/releases/latest))
     - Select an appropriate instance type (at least "t2.small" or similar)
     - Choose your key pair
     - Choose the security group which your created in step 3.
     - For the storage we recommend to keep the pre-selected 100GB volume
     - Click button "Launch instance"
6. As soon as the machine becomes available you can connect per ssh with user `ubuntu`: `ssh -i your_key.pem ubuntu@the_new_ec_instance`

## Login

See [Login to AMI and VM Editions](login-vm-and-ami.md) for logging in to the system.
