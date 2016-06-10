#!/usr/bin/env bash

pushd .

# Check OS
. setup_detectOS.sh

# Figure out where we are
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ALTENV_VENV="${HOME}/.virtualenvs/altEnv"
ERROR_LOG="${DIR}/error.log"
PKG_CONFIG_DIR="${DIR}/include/lib/pkgconfig"

# Make the includes dir
mkdir ${DIR}/builds 2>/dev/null
mkdir -p ${DIR}/include/lib 2>/dev/null


#############
# FUNCTIONS #
#############
# Adding Helper functions here

install_mesa () {
    pushd . 2>/dev/null

    cd ${DIR}/builds

    wget "http://llvm.org/releases/3.8.0/clang+llvm-3.8.0-x86_64-linux-gnu-ubuntu-15.10.tar.xz"
    tar xvvf clang*
    
    cd clang*
    
    LLVM=$PWD
    
    cd ${DIR}/builds

    wget "https://mesa.freedesktop.org/archive/11.2.2/mesa-11.2.2.tar.xz"
    
    tar xvvf mesa-*
    
    cd mesa-*
    
    PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$PKG_CONFIG_DIR ./configure --with-llvm-prefix=$LLVM --disable-llvm-shared-libs --prefix=${DIR}/include 2>> $ERROR_LOG
    
    make -j `nproc` 2>> $ERROR_LOG

    make install 2>> $ERROR_LOG

    # Clean up LLVM
    rm -rf ${DIR}/builds/clang*

    rm -rf ${DIR}/builds/mesa*

    popd 2>/dev/null

}

install_libepoxy () {
    pushd .

    cd ${DIR}/builds
    
    git clone https://github.com/anholt/libepoxy.git 2>> $ERROR_LOG
    
    cd libepoxy
    
    ./autogen.sh --prefix=${DIR}/include 2>> $ERROR_LOG
    
    make -j `nproc` 2>> $ERROR_LOG

    make install 2>> $ERROR_LOG

    rm -rf ${DIR}/builds/libepoxy*

    popd 
}


install_drm () {
    pushd . 

    cd ${DIR}/builds

    # Get latest version
    LIBDRM_VERSION=`curl -s "https://dri.freedesktop.org/libdrm/" | sed -n 's/.*\(libdrm-[0-9\.]*\.tar\.gz\).*/\1/p' | uniq | tail -1`
    
    # Download it
    wget https://dri.freedesktop.org/libdrm/${LIBDRM_VERSION}
    
    # Unpack
    tar zxvvf libdrm-*
    
    cd libdrm-*
    
    ./configure --enable-radeon --enable-amdgpu --enable-nouveau --enable-vmwgfx --prefix=${DIR}/include 2>> $ERROR_LOG
    
    make -j `nproc` 2>> $ERROR_LOG

    make install 2>> $ERROR_LOG

    rm -rf ${DIR}/builds/libdrm*

    popd    
}

install_virglrenderer() {
    pushd .

    cd ${DIR}/builds
    
    git clone git://people.freedesktop.org/~airlied/virglrenderer 2>> $ERROR_LOG
    
    cd virglrenderer
    
    ./autogen.sh 2>> $ERROR_LOG
    
    ./configure --prefix=${DIR}/include 2>> $ERROR_LOG

    make -j `nproc` 2>> $ERROR_LOG

    make install 2>> $ERROR_LOG

    rm -rf ${DIR}/builds/virglrenderer

    popd
}



################
# Main Section #
################



if [[ "$OS" = "linux" ]] && [[ "$DistroBasedOn" = "debian" ]]; then
    sudo apt-get update
    sudo apt-get install -y make gcc virtualenv virtualenvwrapper python3 uuid-dev gcc-aarch64-linux-gnu gcc-arm-linux-gnueabihf git cpu-checker libgtk-3-dev libsdl2-dev libaio-dev libxen-dev libepoxy-dev libdrm-dev libgbm-dev x11proto-dri3-dev x11proto-present-dev libpciaccess-dev libomxil-bellagio-dev xutils-dev curl wget coreutils

    
    # Need to build virglrenderer as Ubuntu only supports it in Yakkety
    install_virglrenderer

    # Debian 16.04 and below don't have the right compiled options in Mesa :(
    install_drm

    # Again, due to Ubuntu's repo not being up-to-date enough
    install_libepoxy

    install_mesa

else
    echo "Don't know prereqs for your distro. You should help me!"
fi

# Setup the venv
mkdir -p $ALTENV_VENV 2>/dev/null

# Setup new virtual environment
virtualenv -p $(which python3) "$ALTENV_VENV" 2>> $ERROR_LOG

# Activate it
source "${ALTENV_VENV}/bin/activate" 2> $ERROR_LOG

# Install requirements
${ALTENV_VENV}/bin/pip install -r ${DIR}/requirements.txt 2>> $ERROR_LOG

cd ${DIR}/MenuSystem-1.3

${ALTENV_VENV}/bin/python setup.py install 2>> $ERROR_LOG

# Build ARM/ARM64 EFI Firmware Images
mkdir -p ${DIR}/firmware ${DIR}/firmware/arm ${DIR}/firmware/aarch64 2>> /dev/null

cd ${DIR}

echo "Building UEFI Firmware Images ... "
git clone git://git.linaro.org/uefi/uefi-tools.git 2>> $ERROR_LOG
git clone https://github.com/tianocore/edk2.git 2>> $ERROR_LOG

cd edk2
../uefi-tools/uefi-build.sh -b RELEASE qemu64 2>> $ERROR_LOG
../uefi-tools/uefi-build.sh -b RELEASE qemu 2>> $ERROR_LOG

# TODO: This is a rather brittle way to match
cp ./Build/ArmVirtQemu-AARCH64/RELEASE_GCC49/FV/QEMU_EFI.fd ${DIR}/firmware/aarch64/. 2>> $ERROR_LOG
cp ./Build/ArmVirtQemu-ARM/RELEASE_GCC49/FV/QEMU_EFI.fd ${DIR}/firmware/arm/. 2>> $ERROR_LOG



popd 2>/dev/null

echo "Install complete."
echo "Remember to activate the altEnv virtualenv before using '$ source ${ALTENV_VENV}/bin/activate)'"
