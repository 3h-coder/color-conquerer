This page covers all topics relative to deploying/serving the web app in a secure way for both the users and the developer, as well as securing the host access.

## Enabling HTTPS with Full SSL/TLS encryption

- Full encryption means the traffic is encrypted between the browser and the cloudflare proxy, and between cloudflare and the VPS as well
![image](https://i.imgur.com/IFnbcqw.png)
- Encryption from the server to the proxy (i.e. cloudflare) is managed by the proxy provider
- To encrypt the traffic from the proxy to the VPS, we must install a certificate on the server. To do so, we're using [certbot](https://certbot.eff.org/). Find below the steps :
  - Install certbot : `sudo apt install certbot python3-certbot-nginx -y`
  - Request a certificate : `sudo certbot --nginx -d your-domain.com -d www.your-domain.com`. This will get a free https certificate from [let's encrypt](https://letsencrypt.org/fr/), configure nginx for https and set up automatic renewals.
  - (optional) Test auto renawal : `sudo certbot renew --dry-run`
  
## Remote access

### Ssh connection

- (Optional) Prefer ssh keys over passwords
- Do not allow logging in with root, instead create a user with admin privileges and log with it. Attackers will now have to guess a username on top of a password.
  - Create the user : `adduser yourusername`
  - Make it admin : `usermod -aG sudo yourusername`
  - Test it : `su - yourusername` `sudo whoami` (should return root)
  - Edit the ssh config (located under `/etc/ssh/sshd_config`) : `PermitRootLogin` -> no
  - Restart ssh : `sudo systemctl restart ssh`

### Fail2Ban

To successfully block brute force attacks, you may use [fail2ban](https://github.com/fail2ban/fail2ban). 
- Install : `sudo apt update` `sudo apt install fail2ban`
- Create a local config (do not edit the default) : `sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local`
- Edit the config : `sudo nano /etc/fail2ban/jail.local`
- In the sshd section, enable the jail : 
```[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = systemd
maxretry = 5
bantime = 3600         # 1 hour
findtime = 600         # 10 minutes
```
- You may check the status at any time : `sudo fail2ban-client status sshd`

  

### Xrdp through ssh tunelling

Because ssh is already highly encrypted and we prefer to avoid exposing the rdp port to the internet, the safest way to access the VPS through xrdp is via ssh tunelling. 
Find below how to setup tunelling through the putty client.

- Configure a xrdp tunnel session through putty. Connection -> SSH -> Tunnels -> Source port: 3389, Destination localhost:3389 -> Add

![image](https://i.imgur.com/6ROcFEb.png)

- Save your session information into a profile for future loading, and open it (this will open up your ssh shell as usual) 

![image](https://i.imgur.com/tKX7UbR.png)

- From your rdp client, simply connect to `localhost:3389`

![image](https://i.imgur.com/nYZ9sxG.png)
![image](https://i.imgur.com/YMFnNhy.png)

## Nginx configuration

### Only allow specific IPs

[TBD]


