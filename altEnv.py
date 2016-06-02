#!/usr/bin/env python3

import menusystem
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
import multiprocessing
from glob import glob
import importlib

CONFIG_FILE = "config.ini"

def installQEMU(_):
    global config
    
    # TODO: Dynamically determine latest qemu version
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
    
    # Run the make using as many cores as we can
    subprocess.check_output("make -j {0}".format(multiprocessing.cpu_count()),shell=True,cwd=os.path.join(config['global']['base_path'],qemu_version,"build"))
    
    # Update the config
    config['global']['qemu-img'] = os.path.join(config['global']['base_path'],qemu_version,"build","qemu-img")
    config['global']['qemu-system-mips'] = os.path.join(config['global']['base_path'],qemu_version,"build","mips-softmmu","qemu-system-mips")
    
    sys.stdout.write(green("[ Completed ]\n"))

    # Update config with the new info
    writeConfig()

    
    input("Press Any Key To Continue")

def writeConfig():
    global config
    
    #with open(os.path.join(config['global']['base_path'],CONFIG_FILE),"w") as f:
    with open(CONFIG_FILE,"w") as f:
        config.write(f)

    # Create needed output dirs
    os.makedirs(os.path.join(config['global']['base_path'],"environments"),exist_ok=True)


def updateConfig(_):
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

def selectOS(arch):
    """
    Given arch (i.e.: MIPS), return menu for selecting valid Operating Systems
    """
    os_items = []
    
    index = 1

    # Dynamically populate what architectures we have (<installers>/*)
    for host_os in glob(os.path.join(config['global']['base_path'],"installers",arch,"*")):
        host_os = os.path.splitext(os.path.basename(host_os))[0]
        if host_os == "__pycache__":
            continue

        # TODO: Maybe import here?
        os_items.append(menusystem.Choice(selector=index, value=index, handler=importlib.import_module("installers.{0}.{1}".format(arch,host_os)).setup, description=host_os))
        index += 1
    
    #items = []
    #items.append(menusystem.Choice(selector=1, value=1, handler=None, description='MIPS'))
    os_items.append(menusystem.Choice(selector=0, value=0, handler=lambda _: False, description='Back'))

    menu = menusystem.MenuSystem.Menu(title='Operating System', choice_list=os_items, prompt='Select Choice.> ') 
    
    return menu

def selectArch():
    arch_items = []
    
    index = 1

    # Dynamically populate what architectures we have (<installers>/*)
    for arch in glob(os.path.join(config['global']['base_path'],"installers","*")):
        arch = os.path.basename(arch)
        if arch == "__pycache__":
            continue

        # Recursively populate the menu
        arch_items.append(menusystem.Choice(selector=index, value=index, handler=None, description=arch, subMenu=selectOS(arch)))
        index += 1
    
    #items = []
    #items.append(menusystem.Choice(selector=1, value=1, handler=None, description='MIPS'))
    arch_items.append(menusystem.Choice(selector=0, value=0, handler=lambda _: False, description='Back'))

    menu = menusystem.MenuSystem.Menu(title='Architecture', choice_list=arch_items, prompt='Select Choice.> ') 
    
    return menu

def mainMenu():

    arch_items = []


    items = []
    items.append(menusystem.Choice(selector=1, value=1, handler=lambda _: print() or print(getStatus()), description='Check status of altEnv'))
    items.append(menusystem.Choice(selector=2, value=2, handler=updateConfig, description='Update altEnv Config'))
    items.append(menusystem.Choice(selector=3, value=3, handler=installQEMU, description='Install QEMU'))
    items.append(menusystem.Choice(selector=4, value=4, handler=None, description='Run Environment'))
    items.append(menusystem.Choice(selector=5, value=5, handler=None, description='Create Environment',subMenu=selectArch()))
    items.append(menusystem.Choice(selector=0, value=0, handler=lambda _: exit(0), description='Exit'))

    #status = FunctionItem("Status",lambda: print(getStatus()) or input())
    #update_config = FunctionItem("Update Config",updateConfig)
    #install_qemu = FunctionItem("Install QEMU",installQEMU)
    #run = MenuItem("Run Environment")
    #create = FunctionItem("Create Environment",selectArch)
    
    
    """
    selectArch = CursesMenu("altEnvs v0.1", "Select Architecture") 
    arch_mips = FunctionItem("MIPS",selectOS,"MIPS")
    selectArch.append_item(arch_mips)
    create = SubmenuItem("Create Environment",selectArch)
    """
    
    menu = menusystem.MenuSystem.Menu(title='Main Menu', choice_list=items, prompt='Select Choice.> ') 
    #menu.append_item(status)
    #menu.append_item(update_config)
    #menu.append_item(install_qemu)
    #menu.append_item(run)
    #menu.append_item(create)
    menu.waitForInput()

"""
def selectArch():
    menu = CursesMenu("altEnvs v0.1", "Select Desired Architecture")

    mips = FunctionItem("MIPS",selectMIPSOS)

    menu.append_item(mips)
    
    menu.show()


def selectMIPSOS():
    menu = CursesMenu("altEnvs v0.1", "Select OS for MIPS")

    mips = FunctionItem("MIPS",selectMIPSOS)

    menu.append_item(mips)
    
    menu.show()
"""
    

def hasQEMU():
    """
    Returns Bool of if qemu is accessible to the program
    """
    qemu = shutil.which("qemu-img")
    
    return True if qemu != None else False

def getTools():
    """
    Returns a dictionary of tool paths. Prioritize tools that we explicitly set.
    """

    tools = {}
    tools['qemu-img'] = config['global']['qemu-img'] if config['global']['qemu-img'] is not "" else shutil.which("qemu-img")
    tools['qemu-system-mips'] = config['global']['qemu-system-mips'] if config['global']['qemu-system-mips'] is not "" else shutil.which("qemu-system-mips")
    
    return tools
    

def getStatus():
    """
    Create a status table.
    Returns PrettyTable object
    """
    t = PrettyTable(["attribute","value"])
    t.header = False

    # Check for QEMU
    #qemu = hasQEMU()
    tools = getTools()
    
    # If qemu is found, grab the version
    if tools['qemu-img'] is not None:
        qemu_vers = subprocess.check_output("{0} --version".format(tools['qemu-img']),shell=True).decode('ascii')
        qemu_vers = re.search("qemu-img version (.+),",qemu_vers).group(1)
        qemu = green("Found: Version {0}".format(qemu_vers))
    
    # If qemu isn't found, print error
    else:
        qemu = red("QEMU not found!")
    
    t.add_row(["QEMU",qemu])
    
    return t

readConfig()

#menu = CursesMenu("altEnvs v0.1", "")

mainMenu()

#menu.show()

