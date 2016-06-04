#!/usr/bin/env bash

# Check OS
. setup_detectOS.sh

if [[ "$OS" = "linux" ]] && [[ "$DistroBasedOn" = "debian" ]]; then
    sudo apt-get update
    sudo apt-get install -y make gcc virtualenv virtualenvwrapper python3 uuid-dev gcc-aarch64-linux-gnu gcc-arm-linux-gnueabihf git
else
    echo "Don't know prereqs for your distro. You should help me!"
fi

# Figure out where we are
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ALTENV_VENV="${HOME}/.virtualenvs/altEnv"
ERROR_LOG="${DIR}/error.log"

# Setup the venv
mkdir -p $ALTENV_VENV 2>/dev/null

# Setup new virtual environment
virtualenv -p $(which python3) "$ALTENV_VENV" 2> $ERROR_LOG

# Activate it
source "${ALTENV_VENV}/bin/activate" 2> $ERROR_LOG

# Install requirements
${ALTENV_VENV}/bin/pip install -r ${DIR}/requirements.txt 2> $ERROR_LOG

pushd .
cd ${DIR}/MenuSystem-1.3

${ALTENV_VENV}/bin/python setup.py install 2> $ERROR_LOG

# Build ARM/ARM64 EFI Firmware Images
mkdir -p ${DIR}/firmware ${DIR}/firmware/arm ${DIR}/firmware/aarch64 2> /dev/null

cd ${DIR}

git clone git://git.linaro.org/uefi/uefi-tools.git 2> $ERROR_LOG
git clone https://github.com/tianocore/edk2.git 2> $ERROR_LOG

cd edk2
../uefi-tools/uefi-build.sh -b RELEASE qemu64 2> $ERROR_LOG
../uefi-tools/uefi-build.sh -b RELEASE qemu 2> $ERROR_LOG

# TODO: This is a rather brittle way to match
cp ./Build/ArmVirtQemu-AARCH64/RELEASE_GCC49/FV/QEMU_EFI.fd ${DIR}/firmware/aarch64/. 2> $ERROR_LOG
cp ./Build/ArmVirtQemu-ARM/RELEASE_GCC49/FV/QEMU_EFI.fd ${DIR}/firmware/arm/. 2> $ERROR_LOG



popd 2>/dev/null

echo "Install complete."
echo "Remember to activate the altEnv virtualenv before using '$ source ${ALTENV_VENV}/bin/activate)'"
