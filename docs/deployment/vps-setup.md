This page is a comprehensive guide regarding all the necessary steps to deploy the app over the internet, in the most efficient way possible. It goes along with the [security.md](./security.md) guide file

## Getting a VPS

- Any vps is fine, as long as it is linux and has a minimum of 2 cores and 8gbs of ram
- Decent providers include [contabo](https://contabo.com/en/), [hetzner](https://www.hetzner.com/), [ovh](https://www.ovhcloud.com/en/) etc.

## Domain configuration

- Get the domain name at a registrar. I personally went for [cloudflare](https://www.cloudflare.com/) as their free tier is pretty good a,d wanted to take advantage of their other services, but there are many ([godaddy](https://www.godaddy.com), [namecheap](https://www.namecheap.com/), [squarespace](https://domains.squarespace.com/), etc.)
- Map the domain name to your VPS' public IP, by creating two A records : one for your domain, and one for www. Here's how it looks like in the cloudflare dashboard.
![image](https://i.imgur.com/iUsUcik.png)

## Remote access

### Installing a GUI

Even a cheap VPS can handle (not so smoothly though) a lightweight GUI as long as it has decent RAM and CPU. I personally went for [lubuntu](https://www.lubuntu.fr/).

- Upgrade the package manager : `sudo apt update && sudo apt upgrade`
- Install lubuntu : `sudo apt install lubuntu-desktop`
- Restart : `sudo reboot`

### Access the remote server terminal through ssh (for Windows)

If on a Windows machine, you'll establish the ssh connection with the help of [putty](https://www.putty.org/).
Once you've installed putty, please do the steps below. Make sure that the ssh port is enabled on the VPS.

- To connect to the terminal, simply enter the IPV4 address
![image](https://i.imgur.com/LNZ1Mf8.png)

### Installing XRDP (to access it from a Windows machine)

- Upgrade the package manager : `sudo apt update && sudo apt upgrade`
- Install xrdp : `sudo apt install xrdp`
- Enable xrdp : `sudo systemctl enable xrdp`
- Start xrdp : `sudo systemctl status xrdp`
- (Optional) Configure xrdp to use the LXQt session (for lubuntu) : `echo "lxqt-session" > ~/.xsession
`
- (Optional) allow xrdp through the firewall : `sudo ufw allow 3389/tcp`
- (Optional) add the user to the sll-cert group : `sudo adduser xrdp ssl-cert`
- Restart xrdp : `sudo systemctl restart xrdp`

After all of this, you may connect from a Windows machine using the built in Remote Desktop Connection (mstsc), or using a rdp client like [freerdp](https://www.freerdp.com/).

For increased security, it's better to access the VPS through ssh tunelling for the packets to be encrypted. Find details in [this section](./security.md#xrdp-through-ssh-tunelling).

## Firewall setup

A good firewall command line tool is [ufw](https://help.ubuntu.com/community/UFW). By default, all ports and connections are closed except the ones explicitly allowed in the defined rules. You may check the rules with `sudo ufw status verbose`.
The following rules should be put in place :
- Allow ssh from anywhere - 22, 22/tcp, v6 included. This is to access the server remotely as a user.
- Allow http/https from anywhere - 80, 443, 80/tcp, 443/tcp, v6 included. This is to properly serve the web app.
Please refer to the [Nginx](#nginx) setup section for that.

You do not need, and should not have any other port exposed and listening to incoming public connections. Please refer to the [security.md](./security.md) file for strong firewall security. 


## Nginx 

We're using [nginx](https://nginx.org/en/) as our reverse proxy to route the requests to our front-end or back-end servers.

### Installation 

Find below the setup steps
- Install nginx : `sudo apt install nginx -y`
- Enable nginx : `sudo systemctl enable nginx`
- Start nginx : `sudo systemctl start nginx`
- Apply the nginx firewall profile : `sudo ufw allow 'Nginx Full'` This applies a predefined ufw application profile (found in `/etc/ufw/applications.d/`) which typically allows for 80 and 443 listening.

### Configuration

[TBD]

## App depencencies

Note that python is already installed by default on ubuntu.
The script will automatically setup the venv and install the python dependencies before running the web app.
Check the [serve](#serve-the-web-app) section for that.

### Npm

Find the steps below to install npm:
- Update apt : `sudo apt update`
- Install : `sudo apt install npm`

### Redis

Find the steps below to install redis :
- Install : `sudo apt install redis-server -y`
- Enable : `sudo systemctl enable redis-server`
- Start : `sudo systemctl start redis-server`
- Check status : `sudo systemctl status redis-server`
- Test redis :  `redis-cli` `ping` (should return "PONG")

### PostgreSQL

Find the steps below to install postgre sql:
- Install : `sudo apt install postgresql postgresql-contrib -y`
- Enable : `sudo systemctl enable postgresql`
- Start : `sudo systemctl start postgresql`

I personally prefer to use a GUI for managing databases, so I chose to install pgAdmin4.
- Install the public key for the repo : `curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo apt-key add`
- Create the repo configuration file : `sudo sh -c 'echo "deb https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'`
- Install pgAdmin for desktop : `sudo apt install pgadmin4-desktop`

Now setup a password for the postgres superuser
- Connect to psql as postgres : `sudo -u postgres psql`
- Change the password : `\password postgres`
You may now connect to the server in pgAdmin4, see the default postgres database and create the database for the web app.

## Serve the web app

### Getting the production version through git