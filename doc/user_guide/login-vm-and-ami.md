## Login to AMI and VM Editions

<!-- I assume the login user for AMI and VM Editions is still ubuntu. -->
<!-- Can and/or should we try to enforce password change for user jupyter, too? -->
Username: **ubuntu**

At the first login to the AI-Lab (image or AMI) you will be prompted to change your password.
The default password is: **ailab**

However, we suggest to use ssh-keys for the connection. When you use the AWS AMI, this will work automatically. When using the VM images, you need to deploy your ssh-keys. After you enabled ssh-keys, we recommend to disable ssh password authentication:
```shell
sudo sed -i "s/PasswordAuthentication yes/PasswordAuthentication no/g" /etc/ssh/sshd_config
sudo systemctl restart ssh.service
```
