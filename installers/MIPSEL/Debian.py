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
    """
    print()

    x = ""

    while x not in ['stable','testing',"unstable"]:
        x = input("Which distro? Stable/Testing/Unstable? ").lower()    

    base_url = "http://ftp.us.debian.org/debian/dists/{0}/main/installer-mipsel/current/images/malta/netboot/".format(x)

    config = readConfig()
    tools = getTools()

    env_name, full_env_path, hd_size, smp, memory, input_type, optimize  = getVMVariables(input_recommend="console")

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
    sys.stdout.flush()

    if optimize:
        subprocess.check_output("{2} create -f raw {0} {1}".format(os.path.join(full_env_path,"hda.img"),hd_size,tools['qemu-img']),shell=True)
    else:
        subprocess.check_output("{2} create -f qcow {0} {1}".format(os.path.join(full_env_path,"hda.img"),hd_size,tools['qemu-img']),shell=True)


    sys.stdout.write(green("[ Completed ]\n"))
  
    sys.stdout.write("Building config file ... ")
    
    options = {
        #'M': 'malta,accel=kvm:xen:tcg',
        'append': "'root=/dev/sda1 console=ttyS0'",
        'kernel': '$ENV_PATH/' + vmlinux,
        'm': memory,
        'cpu': '5KEf',
        #'hda': '$ENV_PATH/hda.img'
    }

    if optimize:
        options['drive'] = 'file=$ENV_PATH/hda.img,if=virtio,cache=writeback,format=raw'
        drive = "-drive {0}".format(options['drive'].replace("$ENV_PATH",full_env_path))

        options['M'] = "malta,accel=kvm:xen:tcg"
        M = "-M {0}".format(options['M'])

    else:
        options['hda'] = '$ENV_PATH/hda.img'
        drive = "-hda {0}".format(options['hda'].replace("$ENV_PATH",full_env_path))

        options['M'] = "malta"
        M = "-M malta"


    input_option = writeVMConfig(env_path=full_env_path,tool="qemu-system-mips64el",input_type=input_type,options=options)

    sys.stdout.write(green("[ Completed ]\n"))

    print("Starting setup ... ") 
    
    # Run system to initiate setup
    # Removing SMP for now as it isn't running correctly with that option
    # Also removing memory options. Both seem to either break or have no effect
    os.system("{0} {7} -cpu 5KEf -kernel {1} -initrd {2} {3} -append \"root=/dev/ram console=ttyS0\" {6}".format(
        tools['qemu-system-mips64el'],
        os.path.join(full_env_path,vmlinux),
        os.path.join(full_env_path,"initrd.gz"),
        #os.path.join(full_env_path,"hda.img"),
        drive,
        smp,
        memory,
        input_option,
        M
        ))
