#!/usr/bin/env python3

import sys
import lzma
import subprocess
from helpers import *
import re
import urllib
import os.path
import os
from tcolors import *
import configparser
import multiprocessing
import shutil

NAME = "Debian ARM64"
DESCRIPTION = "Installer for Debian running on an emulated ARM64 Processor"


def setup(_):
    """Walk the user through setting up a Debian ARM64 environment
    """

    print(red("""
###########
# Warning #
###########
To successfully use this installer you need to follow the guidance posted on: https://gmplib.org/~tege/qemu.html (block 14). This requires a few extra steps before rebooting to ensure that this device can be used

An ssh forward is automatically created for you. Use 'ssh -p 2222 USER@localhost' for your ssh commands"
"""))

    if input(red("Still Proceed [y/N]? ")).lower() != "y":
        return


    x = ""
    while x not in ['stable','testing',"unstable"]:
        x = input("Which distro? Stable/Testing/Unstable? ").lower()    

    base_url = "http://ftp.us.debian.org/debian/dists/{0}/main/installer-arm64/current/images/netboot/debian-installer/arm64/".format(x)

    config = readConfig()
    tools = getTools()

    env_name, full_env_path, hd_size, smp, memory, input_type = getVMVariables()

    with urllib.request.urlopen(base_url) as u:
        html = u.read()


    # Figure out the versions
    #vmlinux = re.search(b"<a href=\"(vmlinux.*?)\">",html).group(1).decode('ascii')
    
    sys.stdout.write("\nDownloading linux kernel ... ")
    sys.stdout.flush()

    # Download vmlinux file
    urllib.request.urlretrieve(base_url + "linux",os.path.join(full_env_path,"linux"))
    
    sys.stdout.write(green("[ Completed ]\n"))

    sys.stdout.write("Downloading initrd.gz ... ")
    sys.stdout.flush()
    
    # Download initrd.gz
    urllib.request.urlretrieve(base_url + "initrd.gz",os.path.join(full_env_path,"initrd.gz"))

    sys.stdout.write(green("[ Completed ]\n"))

    # Copy over UEFI image
    sys.stdout.write("Copying UEFI image ... ")
    sys.stdout.flush()

    bios_path = os.path.join(config['global']['base_path'],"firmware","aarch64","QEMU_EFI.fd")
    shutil.copy(bios_path, full_env_path)
    
    sys.stdout.write(green("[ Completed ]\n"))

    sys.stdout.write("Creating virtual hard drive ... ")
    # TODO: Probably should check output
    subprocess.check_output("{2} create -f qcow {0} {1}".format(os.path.join(full_env_path,"hda.img"),hd_size,tools['qemu-img']),shell=True)

    sys.stdout.write(green("[ Completed ]\n"))
  
    sys.stdout.write("Building config file ... ")
    
    options = {
        'M': 'virt,accel=kvm:xen:tcg',
        'append': "'root=/dev/vda2'",
        'kernel': "$ENV_PATH/linux",
        'initrd': "$ENV_PATH/initrd.gz",
        'm': memory,
        'cpu': 'cortex-a57',
        'device': 'virtio-net-device,netdev=mynet0 -device virtio-blk-device,drive=blk',
        'netdev': 'user,id=mynet0,net=192.168.76.0/24,dhcpstart=192.168.76.9',
        'smp': str(smp),
        'bios': "$ENV_PATH/QEMU_EFI.fd",
    }
    
    input_option = writeVMConfig(env_path=full_env_path,tool="qemu-system-aarch64",input_type=input_type,options=options)

    sys.stdout.write(green("[ Completed ]\n"))

    print("Starting setup ... ") 
    
    # Run system to initiate setup
    os.system("{0} -M virt,accel=kvm:xen:tcg -cpu cortex-a57 -kernel {1} -initrd {2} -smp {4} -m {5} -device virtio-net-device,netdev=mynet0 -netdev user,id=mynet0,net=192.168.76.0/24,dhcpstart=192.168.76.9,hostfwd=tcp::2222-:22 -bios {7} -drive file={3},if=none,id=blk -device virtio-blk-device,drive=blk {6}".format(
        tools['qemu-system-aarch64'],
        os.path.join(full_env_path,"linux"),
        os.path.join(full_env_path,"initrd.gz"),
        os.path.join(full_env_path,"hda.img"),
        smp,
        memory,
        input_option,
        bios_path
        ))
