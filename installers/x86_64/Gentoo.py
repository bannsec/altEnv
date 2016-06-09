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

NAME = "Gentoo x86_64"
DESCRIPTION = "Installer for Gentoo running on an emulated x86_64 Processor"


def setup(_):
    """Walk the user through setting up an Gentoo x86_64 environment
    """
    print()

    config = readConfig()
    tools = getTools()

    env_name, full_env_path, hd_size, smp, memory, input_type, optimize = getVMVariables(input_recommend="gtk")

    # Find the current versions
    with urllib.request.urlopen("http://distfiles.gentoo.org/releases/amd64/autobuilds/latest-install-amd64-minimal.txt") as f:
        html = f.read()

    # Find the current one
    current = re.search(b"[0-9a-zA-Z/\-]+\.iso",html).group(0).decode('ascii')

    url = "http://distfiles.gentoo.org/releases/amd64/autobuilds/{0}".format(current)

    sys.stdout.write("\nDownloading Boot ISO ... ")
    sys.stdout.flush()

    # Download iso file
    urllib.request.urlretrieve(url,os.path.join(full_env_path,"boot.iso"))
    
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
    }

    if optimize:
        options['drive'] = 'file=$ENV_PATH/hda.img,if=virtio,cache=writeback,format=raw'
        drive = "-drive {0}".format(options['drive'].replace("$ENV_PATH",full_env_path))

        options['M'] = "'pc,accel=kvm:xen:tcg'"
        M = "-M {0}".format(options['M'])

    else:
        options['hda'] = '$ENV_PATH/hda.img'
        drive = "-hda {0}".format(options['hda'].replace("$ENV_PATH",full_env_path))

        M = ""


    input_option = writeVMConfig(env_path=full_env_path,tool="qemu-system-x86_64",input_type=input_type,options=options)

    sys.stdout.write(green("[ Completed ]\n"))

    print("Starting setup ... ") 
    
    # Run system to initiate setup
    os.system("{0} {1} {6} -cdrom {2} -smp {3} -m {4} {5}".format(
        tools['qemu-system-x86_64'],
        #os.path.join(full_env_path,"hda.img"),
        drive,
        os.path.join(full_env_path,"boot.iso"),
        1, # Looks like the installer isn't working right with SMP smp,
        memory,
        input_option,
        M
        ))
