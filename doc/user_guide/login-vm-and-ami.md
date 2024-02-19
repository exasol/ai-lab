## Login to AMI and VM Editions

Username: **ubuntu**

At the first login to the sandbox (image or AMI) you will be prompted to change your password.
The default password is: **ai-lab**

However, we suggest to use ssh-keys for the connection. When you use the AWS AMI, this will work automatically. When using the VM images, you need to deploy your ssh-keys. After you enabled ssh-keys, we recommend to disable ssh password authentication:
```shell
sudo sed -i "s/PasswordAuthentication yes/PasswordAuthentication no/g" /etc/ssh/sshd_config
sudo systemctl restart ssh.service
```
