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

NAME = "Arch Linux x86_64"
DESCRIPTION = "Installer for Arch Linux running on an emulated x86_64 Processor"


def setup(_):
    """Walk the user through setting up an Arch Linux x86_64 environment
    """
    print()

    url = "https://releng.archlinux.org/pxeboot/ipxe_text.lkrn"

    config = readConfig()
    tools = getTools()

    env_name, full_env_path, hd_size, smp, memory = getVMVariables()

    sys.stdout.write("\nDownloading PXE Boot ... ")
    sys.stdout.flush()

    # Download vmlinux file
    urllib.request.urlretrieve(url,os.path.join(full_env_path,"ipxe_text.lkrn"))
    
    sys.stdout.write(green("[ Completed ]\n"))

    sys.stdout.write("Creating virtual hard drive ... ")
    # TODO: Probably should check output
    subprocess.check_output("qemu-img create -f qcow {0} {1}".format(os.path.join(full_env_path,"hda.img"),hd_size),shell=True)

    sys.stdout.write(green("[ Completed ]\n"))
  
    sys.stdout.write("Building config file ... ")
    

    vm_config = configparser.ConfigParser()
    vm_config.optionxform = str 
    vm_config.add_section('global')
    vm_config['global']['tool'] = "qemu-system-x86_64"
    vm_config.add_section('options')
    #vm_config['options']['M'] = "malta"
    #vm_config['options']['append'] = "'root=/dev/sda1 console=ttyS0'"
    vm_config['options']['nographic'] = ""
    #vm_config['options']['kernel'] = vmlinux
    vm_config['options']['smp'] = str(smp)
    vm_config['options']['m'] = memory
    vm_config['options']['display'] = "curses"
    vm_config['options']['vga'] = "vmware"
    vm_config['options']['full-screen'] = ""

    with open(os.path.join(full_env_path,"config.ini"),"w") as f:
        vm_config.write(f)

    sys.stdout.write(green("[ Completed ]\n"))

    print("Starting setup ... ") 
    
    # Run system to initiate setup
    os.system("{0} -hda {1} -nographic -kernel {2} -smp {3} -m {4} -display curses -vga vmware -full-screen".format(
        tools['qemu-system-x86_64'],
        os.path.join(full_env_path,"hda.img"),
        os.path.join(full_env_path,"ipxe_text.lkrn"),
        smp,
        memory
        ))
