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


CONFIG_FILE = "config.ini"


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
    config['global']['qemu_path'] = ""
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
    install_qemu = MenuItem("Install QEMU")
    run = MenuItem("Run Environment")

    menu.append_item(status)
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

