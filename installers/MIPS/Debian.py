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

    # TODO: This ins't terribly pythonic...
    while True:
        env_name = input("Name your environment: ")
        # Full path to this new environment
        full_env_path = os.path.join(config['global']['base_path'],"environments",env_name)
        if os.path.exists(full_env_path):
            print("This environment name already exists. Try again.")
            continue
        else:
            # Create the new env
            os.mkdir(full_env_path)
            break
    
    # How big should the hard drive be 
    hd_size = input("Hard Drive Size [2G]: ")
    # Default size of 2G
    hd_size = hd_size if hd_size is not "" else "2G"

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
   
    print("Starting setup ... ") 
    
    # Run system to initiate setup
    os.system("{0} -M malta -kernel {1} -initrd {2} -hda {3} -append \"root=/dev/ram console=ttyS0\" -nographic".format(
        tools['qemu-system-mips'],
        os.path.join(full_env_path,vmlinux),
        os.path.join(full_env_path,"initrd.gz"),
        os.path.join(full_env_path,"hda.img")
        ))
