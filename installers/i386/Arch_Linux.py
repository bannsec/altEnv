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

NAME = "Arch Linux x86"
DESCRIPTION = "Installer for Arch Linux running on an emulated x86 Processor"


def setup(_):
    """Walk the user through setting up an Arch Linux x86 environment
    """
    print()

    config = readConfig()
    tools = getTools()

    env_name, full_env_path, hd_size, smp, memory, input_type, optimize = getVMVariables()

    # Find the current url
    with urllib.request.urlopen("https://www.archlinux.org/releng/netboot/") as f:
        html = f.read()

    # Parse it out
    url = re.search(b"href=['\"](.*?)['\"]>ipxe.lkrn",html).group(1).decode('ascii')

    sys.stdout.write("\nDownloading PXE Boot ... ")
    sys.stdout.flush()

    # Download vmlinux file
    urllib.request.urlretrieve(url,os.path.join(full_env_path,"ipxe.lkrn"))
    
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
        'M': 'pc,accel=kvm:xen:tcg',
    }

    if optimize:
        options['drive'] = 'file=$ENV_PATH/hda.img,if=virtio,cache=writeback,format=raw'
        drive = "-drive {0}".format(options['drive'].replace("$ENV_PATH",full_env_path))
    else:
        options['hda'] = '$ENV_PATH/hda.img'
        drive = "-hda {0}".format(options['hda'].replace("$ENV_PATH",full_env_path))


    input_option = writeVMConfig(env_path=full_env_path,tool="qemu-system-i386",input_type=input_type,options=options)

    sys.stdout.write(green("[ Completed ]\n"))

    print("Starting setup ... ") 
    
    # Run system to initiate setup
    os.system("{0} -M pc,accel=kvm:xen:tcg {1} -kernel {2} -smp {3} -m {4} {5}".format(
        tools['qemu-system-i386'],
        #os.path.join(full_env_path,"hda.img"),
        drive,
        os.path.join(full_env_path,"ipxe.lkrn"),
        smp,
        memory,
        input_option
        ))
