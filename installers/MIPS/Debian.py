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
    
     Parameters
     ----------
     config : dict
        Dictionary object containing parsed config values
    """
    
    base_url = "http://ftp.de.debian.org/debian/dists/stable/main/installer-mips/current/images/malta/netboot/"

    config = readConfig()
    tools = getTools()

    env_name, full_env_path, hd_size, smp, memory = getVMVariables()

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
    subprocess.check_output("qemu-img create -f qcow {0} {1}".format(os.path.join(full_env_path,"hda.img"),hd_size),shell=True)

    sys.stdout.write(green("[ Completed ]\n"))
  
    sys.stdout.write("Building config file ... ")
    

    vm_config = configparser.ConfigParser()
    vm_config.optionxform = str 
    vm_config.add_section('global')
    vm_config['global']['tool'] = "qemu-system-mips"
    vm_config.add_section('options')
    vm_config['options']['M'] = "malta"
    vm_config['options']['append'] = "root=/dev/ram console=ttyS0"
    vm_config['options']['nographic'] = ""
    vm_config['options']['smp'] = str(smp)
    vm_config['options']['m'] = memory

    with open(os.path.join(full_env_path,"config.ini"),"w") as f:
        vm_config.write(f)

    sys.stdout.write(green("[ Completed ]\n"))

    print("Starting setup ... ") 
    
    # Run system to initiate setup
    os.system("{0} -M malta -kernel {1} -initrd {2} -hda {3} -append \"root=/dev/ram console=ttyS0\" -nographic -smp {4} -m {5}".format(
        tools['qemu-system-mips'],
        os.path.join(full_env_path,vmlinux),
        os.path.join(full_env_path,"initrd.gz"),
        os.path.join(full_env_path,"hda.img"),
        smp,
        memory
        ))
