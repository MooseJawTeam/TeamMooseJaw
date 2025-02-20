# TeamMooseJaw
Group Repository for COSC 4353 Software Design

## Run Locally
These are instructions for WSL but the process should be similar for Mac/Linux systems.

Note that you'll need to set environment variables with the database username and password. Message `Nightterrors` on Discord to get the username and password for the database.

```
# Open Powershell and enter WSL
wsl

# Clone repo and go to django_app 
git clone https://github.com/Nighttterrors/TeamMooseJaw.git
cd TeamMooseJaw
cd django_app

# Install dependencies if you don't already have them
sudo apt install python3
sudo apt install python3-pip
sudo apt install python3-django
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
sudo apt install python3.10-venv


# Start server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt 
export DB_USER=<USER>
export DB_PASSWORD=<PASSWORD>
python3 manage.py runserver

```
## Query Database 
These are instructions for WSL to connect to the database and run queries. The process should be similar for Mac/Linux Systems.

Message `Nightterrors` on Discord to get the username and password for the database. You'll need them to connect.

```
# Install MySQL cli
sudo apt install mysql-server

# Connect to the database
 mysql --host=moosejawdb.mysql.database.azure.com --user=<USER> --password=<PASSWORD> --port=3306 --database=mjapp
 
# List dbs, tables, and columns
mysql> show databases;
mysql> show tables;
mysql> show columns from users;

# Run query
mysql> select * from users;
 
# Exit
mysql> exit
```

## Ressources
- https://portal.azure.com/#@UofH.UH.EDU/asset/WebsitesExtension/Website/subscriptions/01886e22-9e9c-4375-9a73-0e2188e5aa2d/resourceGroups/TeamMooseJaw_group/providers/Microsoft.Web/sites/TeamMooseJaw
- https://teammoosejaw-c8akbmb3dffbhjct.centralus-01.azurewebsites.net
