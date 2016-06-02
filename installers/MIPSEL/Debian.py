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

NAME = "Debian MIPSEL"
DESCRIPTION = "Installer for Debian running on an emulated MIPSEL (little endian) Processor"


def setup(_):
    """Walk the user through setting up a Debian MIPSEL environment
    
     Parameters
     ----------
     config : dict
        Dictionary object containing parsed config values
    """
    print()

    x = ""

    while x not in ['stable','testing',"unstable"]:
        x = input("Which distro? Stable/Testing/Unstable? ").lower()    

    base_url = "http://ftp.de.debian.org/debian/dists/{0}/main/installer-mipsel/current/images/malta/netboot/".format(x)

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
    vm_config['global']['tool'] = "qemu-system-mips64el"
    vm_config.add_section('options')
    vm_config['options']['M'] = "malta"
    vm_config['options']['append'] = "'root=/dev/sda1 console=ttyS0'"
    vm_config['options']['nographic'] = ""
    vm_config['options']['kernel'] = vmlinux
    #vm_config['options']['smp'] = str(smp)
    #vm_config['options']['m'] = memory

    with open(os.path.join(full_env_path,"config.ini"),"w") as f:
        vm_config.write(f)

    sys.stdout.write(green("[ Completed ]\n"))

    print("Starting setup ... ") 
    
    # Run system to initiate setup
    # Removing SMP for now as it isn't running correctly with that option
    # Also removing memory options. Both seem to either break or have no effect
    os.system("{0} -M malta -kernel {1} -initrd {2} -hda {3} -append \"root=/dev/ram console=ttyS0\" -nographic".format(
        tools['qemu-system-mips64el'],
        os.path.join(full_env_path,vmlinux),
        os.path.join(full_env_path,"initrd.gz"),
        os.path.join(full_env_path,"hda.img"),
        smp,
        memory
        ))
