# Friday
This is a private project that take a dummy sensor and translate their signal to a standard messages that can be stored and later retrieved.

## System Requirements
OS: Linux  
Python: version > 3.6

## Setup environment
The dependency system we used is [poetry](https://github.com/python-poetry/poetry). Follow to their github page to install.

We recommend to use virtualenv to separate the environment from the default python system environment. Follow these steps:
```bash
source ~/.poetry/env
poetry env use system
sudo apt install virtualenv
```

Restart the terminal, then follow to the root directory of the project, then run the follow commands:
```bash
virtualenv -p $(which python3.6) .venv
source .venv/bin/activate
poetry install
```

## Run

The default configuration use MQTT with hostname=localhost, port=1883 as default. If you wish to run with different configuration, use the following command (or just export the environment):
```bash
FRIDAY_HOSTNAME=192.168.1.xx FRIDAY_PORT=1883 make run
```
