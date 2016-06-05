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

    url = "https://releng.archlinux.org/pxeboot/ipxe_text.lkrn"

    config = readConfig()
    tools = getTools()

    env_name, full_env_path, hd_size, smp, memory, input_type = getVMVariables()

    sys.stdout.write("\nDownloading PXE Boot ... ")
    sys.stdout.flush()

    # Download vmlinux file
    urllib.request.urlretrieve(url,os.path.join(full_env_path,"ipxe_text.lkrn"))
    
    sys.stdout.write(green("[ Completed ]\n"))

    sys.stdout.write("Creating virtual hard drive ... ")
    # TODO: Probably should check output
    subprocess.check_output("{2} create -f qcow {0} {1}".format(os.path.join(full_env_path,"hda.img"),hd_size,tools['qemu-img']),shell=True)

    sys.stdout.write(green("[ Completed ]\n"))
  
    sys.stdout.write("Building config file ... ")
    
    options = {
        'm': memory,
        'smp': str(smp),
        'M': 'pc,accel=kvm:xen:tcg',
        'hda': '$ENV_PATH/hda.img'
    }

    input_option = writeVMConfig(env_path=full_env_path,tool="qemu-system-i386",input_type=input_type,options=options)

    sys.stdout.write(green("[ Completed ]\n"))

    print("Starting setup ... ") 
    
    # Run system to initiate setup
    os.system("{0} -M pc,accel=kvm:xen:tcg -hda {1} -nographic -kernel {2} -smp {3} -m {4} {5}".format(
        tools['qemu-system-i386'],
        os.path.join(full_env_path,"hda.img"),
        os.path.join(full_env_path,"ipxe_text.lkrn"),
        smp,
        memory,
        input_option
        ))
