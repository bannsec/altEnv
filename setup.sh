#!/usr/bin/env bash

# Check OS
. setup_detectOS.sh

if [[ "$OS" = "linux" ]] && [[ "$DistroBasedOn" = "debian" ]]; then
    sudo apt-get update
    sudo apt-get install -y make gcc virtualenv virtualenvwrapper python3
else
    echo "Don't know prereqs for your distro. You should help me!"
fi

# Figure out where we are
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

ALTENV_VENV="${HOME}/.virtualenvs/altEnv"

# Setup the venv
mkdir -p $ALTENV_VENV 2>/dev/null

# Setup new virtual environment
virtualenv -p $(which python3) "$ALTENV_VENV"

# Activate it
source "${ALTENV_VENV}/bin/activate"

# Install requirements
${ALTENV_VENV}/bin/pip install -r ${DIR}/requirements.txt

pushd .
cd ${DIR}/MenuSystem-1.3

${ALTENV_VENV}/bin/python setup.py install

popd 2>/dev/null

echo "Install complete."
echo "Remember to activate the altEnv virtualenv before using '$ source ${ALTENV_VENV}/bin/activate)'"
