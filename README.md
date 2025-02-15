# TeamMooseJaw
Group Repository for COSC 4353 Software Design

## Run Locally
These are instructions for WSL but the process should be similar for Mac/Linux systems.

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
pip3 install django
sudo apt install python3-django

# Start server
 python3 manage.py runserver

```