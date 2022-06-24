# BEWA Delivery System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![SERVIR: Global](https://img.shields.io/badge/SERVIR-Global-green)](https://servirglobal.net)
[![conda: conda-forge](https://shields.io/badge/conda%7Cconda--forge-v3.7.1-blue)](https://conda.io/)

This tool enables the https download of the output files from the Bangladesh Extreme Weather Alert system

## Setup and Installation
The installation described here will make use of conda to ensure there are no package conflicts with
existing or future applications on the machine.  It is highly recommended using a dedicated environment
for this application to avoid any issues.

### Recommended
Conda (To manage packages within the applications own environment)

### Environment
- Create the env

```shell
cd bewa_delivery
conda env create -f environment.yml
```

- enter the environment

```shell
conda activate bewa_delivery
```

- Create database tables and superuser
###### follow prompts to create super user
```commandline
python manage.py migrate
python manage.py createsuperuser
```

- Create data.json file to hold your "SECRET_KEY".  You may generate your own random key using letters numbers and 
special characters (56 characters is normal, but you can vary), the file needs to be in bewa_delivery/bewa_delivery 
add the following
```commandline
{
  "SECRET_KEY":"REPLACE WITH A SECRET KEY USING LETTERS, NUMBERS, AND SPECIAL CHARACTERS"
}
```

At this point you should be able to start the application.  From the root directory you can run the following command

```
python manage.py runserver
```

Of course running the application in this manner is only for development.  We recommend installing
this application on a server and serving it through nginx using gunicorn (conda install gunicorn) for production.  To do this you will need to
have both installed on your server.  There are enough resources explaining in depth how to install them,
so we will avoid duplicating this information.  We recommend adding a service to start the application
by creating a .service file located at /etc/systemd/system.  We named ours bewa.service
The service file will contain the following, please substitute the correct paths as mentioned below.

# Server installation
## Create Application Service
As mentioned above create the following file at /etc/systemd/system and name it bewa.service
```editorconfig
[Unit]
Description=bewa_delivery daemon
After=network.target

[Service]
User=nginx
Group=nginx
SocketUser=nginx
WorkingDirectory={REPLACE WITH PATH TO APPLICATION ROOT}/bewa_delivery
accesslog = "/var/log/bewa/bewa_gunicorn.log"
errorlog = "/var/log/bewa/bewa_gunicornerror.log"
ExecStart={REPLACE WITH FULL PATH TO gunicorn IN YOUR CONDA ENV}/bin/gunicorn --timeout 60 --workers 5 --pythonpath '{REPLACE WITH PATH TO APPLICATION ROOT},{REPLACE WITH FULL PATH TO YOUR CONDA ENV}/lib/python3.10/site-packages' --bind unix:{REPLACE WITH LOCATION YOU WANT THE SOCK}/bewa_prod.sock wsgi:application

[Install]
WantedBy=multi-user.target

```
## Create nginx site
Create a file in /etc/nginx/conf.d named bewa_prod.conf

```editorconfig
upstream bewa_prod {
  server unix:{REPLACE WITH LOCATION YOU WANT THE SOCK}/bewa_prod.sock 
  fail_timeout=0;
}

server {
    listen 443;
    server_name {REPLACE WITH YOUR DOMAIN};
    add_header Access-Control-Allow-Origin *;

    ssl on;
    ssl_certificate {REPLACE WITH FULL PATH TO CERT FILE};
    ssl_certificate_key {REPLACE WITH FULL PATH TO CERT KEY};

    # Some Settings that worked along the way
    client_max_body_size 8000M;
    client_body_buffer_size 8000M;
    client_body_timeout 120;

    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    fastcgi_buffers 8 16k;
    fastcgi_buffer_size 32k;
    fastcgi_connect_timeout 90s;
    fastcgi_send_timeout 90s;
    fastcgi_read_timeout 90s;


    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        autoindex on;
        alias /bewa_delivery/staticfiles/;
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://unix:{REPLACE WITH LOCATION YOU WANT THE SOCK}/bewa_prod.sock ;
    }


}

# Reroute any non https traffic to https
server {
    listen 80;
    server_name {REPLACE WITH YOUR DOMAIN};
    rewrite ^(.*) https://$server_name$1 permanent;
}

```
# Create Alias commands to make starting the application simple
Create a file at /etc/profile.d named bewa_alias.sh and add the following:
```editorconfig
alias bewa='cd /servir_apps/bewa'
alias actbewa='conda activate bewa_delivery'
alias uobewa='sudo chown -R ${USER} /servir_apps/bewa_delivery'
alias sobewa='sudo chown -R www-data /servir_apps/bewa_delivery'
alias bewastart='sudo service bewa restart; sudo service nginx restart; so'
alias bewastop='sudo service bewa stop'
alias bewarestart='bewastop; bewastart'
```

Now activate the alias file by running
```commandline
source /etc/profile.d/bewa_alias.sh
```

Now you should be able to run bstart to run the production application.  

## Contact

### Authors

- [Billy Ashmall (NASA)](mailto:billy.ashmall@nasa.gov)

## License and Distribution

BEWA Delivery is distributed by SERVIR under the terms of the MIT License. See
[LICENSE](https://github.com/SERVIR/bewa_delivery/blob/master/LICENSE) in this directory for more information.

## Privacy & Terms of Use

BEWA Delivery abides to all of SERVIR's privacy and terms of use as described
at [https://servirglobal.net/Privacy-Terms-of-Use](https://servirglobal.net/Privacy-Terms-of-Use).
