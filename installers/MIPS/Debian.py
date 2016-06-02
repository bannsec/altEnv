#!/usr/bin/env python3

import sys
import lzma
import subprocess
from helpers import *
import re
import urllib

NAME = "Debian MIPS"
DESCRIPTION = "Installer for Debian running on an emulated MIPS Processor"


def setup(_):
    """Walk the user through setting up a Debian MIPS environment
    
     Parameters
     ----------
     config : dict
        Dictionary object containing parsed config values
    """
    readConfig()
    tools = getTools()
    #print(type(tools))

    with urllib.request.urlopen("http://ftp.de.debian.org/debian/dists/stable/main/installer-mips/current/images/malta/netboot/") as u:
        html = u.read()


    # Figure out the versions
    vmlinux = re.search(b"<a href=\"(vmlinux.*?)\">",html).group(1).decode('ascii')
    
    print("\nDownloading {0}".format(vmlinux))


    # Download the needed config files
    # http://ftp.de.debian.org/debian/dists/stable/main/installer-mips/current/images/malta/netboot/

    #sys.stdout.write("Downloading Need Config Files ... ")
    #sys.stdout.flush()
    #urllib.request.urlretrieve("http://wiki.qemu-project.org/download/{0}.tar.bz2".format(qemu_version),os.path.join(config['global']['base_path'],"{0}.tar.bz2".format(qemu_version)))
    #sys.stdout.write(green("[ Completed ]\n"))
    
    sys.stdout.write("Decompressing Archives ... ")
    sys.stdout.flush()

    lzma.decompress

    # Create hard drive space
    #qemu-img create -f qcow hda.img 2G
    
    # In [14]: f = lzma.open("/media/bill/7a704ddd-c815-4d04-9454-5c027f381cb3/QEMU/altEnvs/FreeBSD_i386/FreeBSD-10.3-RELEASE-i386-bootonly.iso.xz")
    # subprocess.check_output("xz -d /media/bill/7a704ddd-c815-4d04-9454-5c027f381cb3/QEMU/altEnvs/FreeBSD_i386/FreeBSD-10.3-RELEASE-i386-bootonly.iso.xz",shell=True)
    #subprocess.check_output("xz -d /media/bill/7a704ddd-c815-4d04-9454-5c027f381cb3/QEMU/altEnvs/FreeBSD_i386/FreeBSD-10.3-RELEASE-i386-bootonly.iso.xz",shell=True,cwd="/media/bill/7a704ddd-c815-4d04-9454-5c027f381cb3/QEMU/altEnvs/FreeBSD_i386/")


    # Run system to initiate setup
    #qemu-system-mips -M malta -kernel vmlinux-<version>-qemu -initrd initrd.gz -hda hda.img -append "root=/dev/ram console=ttyS0" -nographic
