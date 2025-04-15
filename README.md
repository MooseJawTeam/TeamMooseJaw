# TeamMooseJaw
Group Repository for COSC 4353 Software Design

## Run Locally
These are instructions for WSL but the process should be similar for Mac/Linux systems.

Note that you'll need to set environment variables with the database username and password. Message `Nightterrors` on Discord to get the username and password for the database.

```
# Open Powershell and enter WSL
wsl

# Clone repo and go to django_app 
git clone https://github.com/MooseJawTeam/TeamMooseJaw.git
cd TeamMooseJaw
cd django_app

# Install dependencies if you don't already have them
sudo apt install python3
sudo apt install python3-pip
sudo apt install python3-django
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
sudo apt install python3.10-venv
sudo apt-get install libcairo2-dev libpango1.0-dev libgdk-pixbuf2.0-dev libffi-dev shared-mime-info

## Environment Variables
Before running the application, you need to create a `.env` file in the `django_app` directory with the following Microsoft credentials:
```
MSAL_CLIENT_ID=your_client_id
MSAL_CLIENT_SECRET=your_client_secret
MSAL_AUTHORITY=https://login.microsoftonline.com/your_tenant_id
MSAL_REDIRECT_URI=http://localhost:8000/auth/callback
```

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

## Run with Docker
These instructions will help you run the application using Docker and Docker Compose.

### Prerequisites
- Docker installed
- Docker Compose installed
- Git

### Setup Steps
```bash
# Clone the repository
git clone https://github.com/MooseJawTeam/TeamMooseJaw.git
cd TeamMooseJaw
cd django_app

# Build and start the containers
docker-compose build
docker-compose up

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser (optional)
docker-compose exec web python manage.py createsuperuser
```

The application will be available at `http://localhost:8000`

Note: Make sure to update the environment variables in `docker-compose.yml` with your database credentials.
```

## Resources
- [Azure Portal](https://portal.azure.com/#@UofH.UH.EDU/asset/WebsitesExtension/Website/subscriptions/01886e22-9e9c-4375-9a73-0e2188e5aa2d/resourceGroups/TeamMooseJaw_group/providers/Microsoft.Web/sites/TeamMooseJaw)
- [Documentation](UserManagement.md)
