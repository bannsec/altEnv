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
from helpers import *
from natsort import natsort

def installQEMU(_):
    global config

    base_url = "http://wiki.qemu-project.org/download/"

    # Read the directory
    with urllib.request.urlopen(base_url) as f:
        html = f.read()

    versions = natsort.humansorted([x.decode('ascii') for x in list(set(re.findall(b">qemu-([0-9-\.]+?)\.tar\.bz2",html)))])
    
    # Assuming we want the latest version
    qemu_version = versions[-1]

    # TODO: Dynamically determine latest qemu version
    #qemu_version = "qemu-2.6.0"
    
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
    config['global']['qemu-system-mips64'] = os.path.join(config['global']['base_path'],qemu_version,"build"," mips64-softmmu","qemu-system-mips64")
    config['global']['qemu-system-mips64el'] = os.path.join(config['global']['base_path'],qemu_version,"build"," mips64el-softmmu","qemu-system-mips64el")
    
    sys.stdout.write(green("[ Completed ]\n"))

    # Update config with the new info
    writeConfig()

    
    input("Press Any Key To Continue")

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
        os_items.append(menusystem.Choice(selector=index, value=getTools(), handler=importlib.import_module("installers.{0}.{1}".format(arch,host_os)).setup, description=host_os))
        index += 1
    
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
    
    arch_items.append(menusystem.Choice(selector=0, value=0, handler=lambda _: False, description='Back'))

    menu = menusystem.MenuSystem.Menu(title='Architecture', choice_list=arch_items, prompt='Select Choice.> ') 
    
    return menu


def runEnv(env):
    """
    Run the given environment
    """
    
    # First, create variables
    full_env_path = os.path.join(config['global']['base_path'],'environments',env)
    config_path = os.path.join(full_env_path,"config.ini")
    disk_path = os.path.join(full_env_path,"hda.img")
    
    # Figure out what tools to use
    tools = getTools()

    # Load the config
    env_config = configparser.ConfigParser()
    env_config.optionxform = str
    env_config.read(config_path)
    
    # Generate option strings
    options = ""
    for var in env_config['options']:
        # Need to put full path to kernel when we need to use it
        if var == "kernel":
            options += " -kernel {0} ".format(os.path.join(full_env_path,env_config['options'][var]))
        else:
            options += " -{0} {1} ".format(var,env_config['options'][var])
    
    # Tack on the hda
    options += "-hda {0} ".format(os.path.join(full_env_path,"hda.img"))

    command = "{0} {1}".format(tools[env_config['global']['tool']],options)

    #print("Running command: {0}".format(command))
    os.system(command)


def selectVMSubMenu(env):
    
    options = []

    options.append(menusystem.Choice(selector=1, value=env, handler=runEnv, description='Run Environment'))
    options.append(menusystem.Choice(selector=0, value=0, handler=lambda _: False, description='Back'))

    
    menu = menusystem.MenuSystem.Menu(title='{0} Options'.format(env), choice_list=options, prompt='Select Choice.> ') 
    
    return menu


def selectVM():
    """
    Setup Menu for selecting a VM to run
    """
    
    vms = []
    
    index = 1

    # Dynamically populate what architectures we have (<installers>/*)
    for env in glob(os.path.join(config['global']['base_path'],"environments","*")):
        env = os.path.basename(env)
        if env == "__pycache__":
            continue

        # Recursively populate the menu
        vms.append(menusystem.Choice(selector=index, value=index, handler=None, description=env, subMenu=selectVMSubMenu(env)))
        index += 1
    
    vms.append(menusystem.Choice(selector=0, value=0, handler=lambda _: False, description='Back'))

    menu = menusystem.MenuSystem.Menu(title='Environments', choice_list=vms, prompt='Select Choice.> ') 
    
    return menu

def mainMenu():

    arch_items = []


    items = []
    items.append(menusystem.Choice(selector=1, value=1, handler=lambda _: print() or print(getStatus()), description='Check status of altEnv'))
    items.append(menusystem.Choice(selector=2, value=2, handler=updateConfig, description='Update altEnv Config'))
    items.append(menusystem.Choice(selector=3, value=3, handler=installQEMU, description='Install QEMU'))
    items.append(menusystem.Choice(selector=4, value=4, handler=None, description='Run Environment',subMenu=selectVM()))
    items.append(menusystem.Choice(selector=5, value=5, handler=None, description='Create Environment',subMenu=selectArch()))
    items.append(menusystem.Choice(selector=0, value=0, handler=lambda _: exit(0), description='Exit'))

    menu = menusystem.MenuSystem.Menu(title='Main Menu', choice_list=items, prompt='Select Choice.> ') 
    menu.waitForInput()

    

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

global config

config = readConfig()

mainMenu()


