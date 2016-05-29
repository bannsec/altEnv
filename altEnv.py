#!/usr/bin/env python3

from cursesmenu import *
from cursesmenu.items import *
from tcolors import *
from prettytable import PrettyTable
import shutil
import subprocess
import re
import configparser

CONFIG_FILE = "config.ini"

def initConfig():
    global config
    config = configparser.ConfigParser()
    config.add_section('global')
    
    """
    environment-path = /path/to/environment
    qemu-path = /home/blerg
    qemu-img = /path/to/qemu-img
    """


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


menu = CursesMenu("altEnvs v0.1", "")

mainMenu()

menu.show()

