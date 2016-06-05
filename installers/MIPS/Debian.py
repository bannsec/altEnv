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

NAME = "Debian MIPS"
DESCRIPTION = "Installer for Debian running on an emulated MIPS Processor"


def setup(_):
    """Walk the user through setting up a Debian MIPS environment
    """
    print()

    x = ""
    while x not in ['stable','testing',"unstable"]:
        x = input("Which distro? Stable/Testing/Unstable? ").lower()    

    base_url = "http://ftp.us.debian.org/debian/dists/{0}/main/installer-mips/current/images/malta/netboot/".format(x)

    config = readConfig()
    tools = getTools()

    env_name, full_env_path, hd_size, smp, memory, input_type = getVMVariables()

    with urllib.request.urlopen(base_url) as u:
        html = u.read()


    # Figure out the versions
    vmlinux = re.search(b"<a href=\"(vmlinux.*?)\">",html).group(1).decode('ascii')
    
    sys.stdout.write("\nDownloading {0} ... ".format(vmlinux))
    sys.stdout.flush()

    # Download vmlinux file
    urllib.request.urlretrieve(base_url + vmlinux,os.path.join(full_env_path,vmlinux))
    
    sys.stdout.write(green("[ Completed ]\n"))

    sys.stdout.write("Downloading initrd.gz ... ")
    sys.stdout.flush()
    
    # Download initrd.gz
    urllib.request.urlretrieve(base_url + "initrd.gz",os.path.join(full_env_path,"initrd.gz"))

    sys.stdout.write(green("[ Completed ]\n"))

    sys.stdout.write("Creating virtual hard drive ... ")
    # TODO: Probably should check output
    subprocess.check_output("{2} create -f qcow {0} {1}".format(os.path.join(full_env_path,"hda.img"),hd_size,tools['qemu-img']),shell=True)

    sys.stdout.write(green("[ Completed ]\n"))
  
    sys.stdout.write("Building config file ... ")
    
    options = {
        'M': 'malta,accel=kvm:xen:tcg',
        'hda': '$ENV_PATH/hda.img',
        'append': "'root=/dev/sda1 console=ttyS0'",
        'kernel': '$ENV_PATH/' + vmlinux,
        'm': memory,
        'cpu': '5KEf'
    }
    
    input_option = writeVMConfig(env_path=full_env_path,tool="qemu-system-mips64",input_type=input_type,options=options)

    sys.stdout.write(green("[ Completed ]\n"))

    print("Starting setup ... ") 
    
    # Run system to initiate setup
    # Removing SMP for now as it isn't running correctly with that option
    # Also removing memory options. Both seem to either break or have no effect
    os.system("{0} -M malta,accel=kvm:xen:tcg -cpu 5KEf -kernel {1} -initrd {2} -hda {3} -append \"root=/dev/ram console=ttyS0\" -m {5} {6}".format(
        tools['qemu-system-mips64'],
        os.path.join(full_env_path,vmlinux),
        os.path.join(full_env_path,"initrd.gz"),
        os.path.join(full_env_path,"hda.img"),
        smp,
        memory,
        input_option
        ))
