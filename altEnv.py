#!/usr/bin/env python3

from cursesmenu import *
from cursesmenu.items import *
from tcolors import *
from prettytable import PrettyTable
import shutil
import subprocess
import re
import configparser
import os.path
import os
import urllib.request
import sys
import tarfile

CONFIG_FILE = "config.ini"

def installQEMU():
    global config
    
    qemu_version = "qemu-2.6.0"
    
    sys.stdout.write("Downloading QEMU ... ")
    sys.stdout.flush()
    urllib.request.urlretrieve("http://wiki.qemu-project.org/download/{0}.tar.bz2".format(qemu_version),os.path.join(config['global']['base_path'],"{0}.tar.bz2".format(qemu_version)))
    sys.stdout.write(green("[ Completed ]\n"))

    sys.stdout.write("Extracting QEMU ... ")
    sys.stdout.flush()
    
    with tarfile.open("{0}.tar.bz2".format(qemu_version)) as tar:
        tar.extractall()

    sys.stdout.write(green("[ Completed ]\n"))
    
    sys.stdout.write("Compiling QEMU (be patient!) ... ")
    sys.stdout.flush()

    # Make build directory
    os.makedirs(os.path.join(config['global']['base_path'],qemu_version,"build"),exist_ok=True)
    
    # Configure
    try:
        subprocess.check_output("../configure --python=python2",shell=True,cwd=os.path.join(config['global']['base_path'],qemu_version,"build"))
    except Exception as e:
        print(e.output)
        exit(0)
    
    # Run the make
    subprocess.check_output("make",shell=True,cwd=os.path.join(config['global']['base_path'],qemu_version,"build"))
    
    # Update the config
    config['global']['qemu-img'] = os.path.join(config['global']['base_path'],qemu_version,"build","qemu-img")
    config['global']['qemu-system-mips'] = os.path.join(config['global']['base_path'],qemu_version,"build","mips-softmmu","qemu-system-mips")
    
    sys.stdout.write(green("[ Completed ]\n"))

    
    input("Press Any Key To Continue")

def writeConfig():
    global config
    
    with open(os.path.join(config['global']['base_path'],CONFIG_FILE),"w") as f:
        config.write(f)


def updateConfig():
    global config
    
    base_path = input("Base Path [{0}]: ".format(config['global']['base_path']))
    
    if base_path != "":
        config['global']['base_path'] = base_path
    
    writeConfig()


def initConfig():
    global config
    config = configparser.ConfigParser()
    config.add_section('global')

    config['global']['base_path'] = os.path.dirname(os.path.abspath(__file__))
    #config['global']['qemu_path'] = ""
    config['global']['qemu-img'] = ""   
    config['global']['qemu-system-mips'] = ""
    
    writeConfig()    


def readConfig():
    global config
    config = configparser.ConfigParser()
    out = config.read(CONFIG_FILE)

    # If there's no config.ini file, make one
    if out == []:
        initConfig()

def mainMenu():
    menu.items = []
    menu.subtitle = "Main Menu"
    status = FunctionItem("Status",lambda: print(getStatus()) or input())
    update_config = FunctionItem("Update Config",updateConfig)
    install_qemu = FunctionItem("Install QEMU",installQEMU)
    run = MenuItem("Run Environment")

    menu.append_item(status)
    menu.append_item(update_config)
    menu.append_item(install_qemu)
    menu.append_item(run)


def hasQEMU():
    """
    Returns Bool of if qemu is accessible to the program
    """
    qemu = shutil.which("qemu-img")
    
    return True if qemu != None else False

def getStatus():
    """
    Create a status table.
    Returns PrettyTable object
    """
    t = PrettyTable(["attribute","value"])
    t.header = False

    # Check for QEMU
    qemu = hasQEMU()
    
    # If qemu is found, grab the version
    if qemu:
        qemu_vers = subprocess.check_output("qemu-img --version",shell=True).decode('ascii')
        qemu_vers = re.search("qemu-img version (.+),",qemu_vers).group(1)
        qemu = green("Found: Version {0}".format(qemu_vers))
    
    # If qemu isn't found, print error
    else:
        qemu = red("QEMU not found!")
    
    t.add_row(["QEMU",qemu])
    
    return t

readConfig()

menu = CursesMenu("altEnvs v0.1", "")

mainMenu()

menu.show()

