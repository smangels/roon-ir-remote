## Installation

- check whether USB Flir has been connected
- make use of Ansible
- create folder for virtual environment
- deploy virtual environment
- create system user for the remote
- make this user part of "input" group (access to InputDevice)
- generate templates for service file
- copy Python script, owned by new user + group
- reload new service file (sudo systemctl daemon-reload)
- enable and start the new service

