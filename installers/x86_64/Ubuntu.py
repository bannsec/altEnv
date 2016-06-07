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

NAME = "Ubuntu Linux x86_64"
DESCRIPTION = "Installer for Ubuntu Linux running on an emulated x86_64 Processor"


def setup(_):
    """Walk the user through setting up an Ubuntu Linux x86_64 environment
    """
    print()

    # Read in the dists
    with urllib.request.urlopen("http://archive.ubuntu.com/ubuntu/dists/") as f:
        html = f.read()

    # Parse out the valid dists
    dists = [x.decode('ascii').lower() for x in re.findall(b'href="([a-zA-Z]+)/',html)]

    print("Select a distribution to download from: {0}".format(','.join(dists)))

    dist = ""
    # Prompt until we get a valid dist
    while dist not in dists:
        dist = input("Select Distribution: ").lower()

    url = "http://archive.ubuntu.com/ubuntu/dists/{0}/main/installer-amd64/current/images/netboot/mini.iso".format(dist)

    config = readConfig()
    tools = getTools()

    env_name, full_env_path, hd_size, smp, memory, input_type, optimize = getVMVariables(input_recommend="gtk")

    sys.stdout.write("\nDownloading iso ... ")
    sys.stdout.flush()

    # Download vmlinux file
    urllib.request.urlretrieve(url,os.path.join(full_env_path,"mini.iso"))
    
    sys.stdout.write(green("[ Completed ]\n"))

    sys.stdout.write("Creating virtual hard drive ... ")
    sys.stdout.flush()

    if optimize:
        subprocess.check_output("{2} create -f raw {0} {1}".format(os.path.join(full_env_path,"hda.img"),hd_size,tools['qemu-img']),shell=True)
    else:
        subprocess.check_output("{2} create -f qcow {0} {1}".format(os.path.join(full_env_path,"hda.img"),hd_size,tools['qemu-img']),shell=True)

    sys.stdout.write(green("[ Completed ]\n"))
  
    sys.stdout.write("Building config file ... ")
    
    options = {
        'm': memory,
        'smp': str(smp),
        'M': "pc,accel=kvm:xen:tcg",
    }

    if optimize:
        options['drive'] = 'file=$ENV_PATH/hda.img,if=virtio,cache=writeback,format=raw'
        drive = "-drive {0}".format(options['drive'].replace("$ENV_PATH",full_env_path))
    else:
        options['hda'] = '$ENV_PATH/hda.img'
        drive = "-hda {0}".format(options['hda'].replace("$ENV_PATH",full_env_path))

    input_option = writeVMConfig(env_path=full_env_path,tool="qemu-system-x86_64",input_type=input_type,options=options)

    sys.stdout.write(green("[ Completed ]\n"))

    print("Starting setup ... ") 
    
    # Run system to initiate setup
    os.system("{0} {1} -M pc,accel=kvm:xen:tcg -cdrom {2} -smp {3} -m {4} {5}".format(
        tools['qemu-system-x86_64'],
        drive,
        os.path.join(full_env_path,"mini.iso"),
        smp,
        memory,
        input_option
        ))
