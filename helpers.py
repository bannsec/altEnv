import shutil
import configparser
import multiprocessing
import os.path
import os

CONFIG_FILE = "config.ini"


def getVMVariables():

    print("\nInput type defines how you will interact with this VM. The following options are supported by this script:")
    print("\tconsole - This means no graphics support at all. We will attempt to show VM as a console inline")
    print("\tcurses - Use the curses library to translate a virtual display. Again, this will be textual, but more graphical than console")
    print("\tvnc - This will start a VNC server that you can connect to to view the display.")
    print("Note that one might not work for any given reason. It your screen just stays blank, try a different method.")
    
    input_type = ""
    while input_type not in ['console','curses','vnc']:
        input_type = input("Input Type: ").lower()
    

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

    smp = input("Number of CPU Cores [{0}]: ".format(multiprocessing.cpu_count()))
    smp = int(smp) if smp is not "" else multiprocessing.cpu_count()

    memory = input("Memory [1G/1024M]: ")
    memory = memory if memory is not "" else "1G"

    return env_name, full_env_path, hd_size, smp, memory, input_type


def readConfig():
    global config
    config = configparser.ConfigParser()
    out = config.read(CONFIG_FILE)

    # If there's no config.ini file, make one
    if out == []:
        initConfig()
    
    return config

def getTools():
    """
    Returns a dictionary of tool paths. Prioritize tools that we explicitly set.
    """

    tools = {}
    tools['qemu-img'] = config['global']['qemu-img'] if config['global']['qemu-img'] is not "" else shutil.which("qemu-img")
    tools['qemu-system-mips'] = config['global']['qemu-system-mips'] if config['global']['qemu-system-mips'] is not "" else shutil.which("qemu-system-mips")
    tools['qemu-system-mips64'] = config['global']['qemu-system-mips64'] if config['global']['qemu-system-mips64'] is not "" else shutil.which("qemu-system-mips64")
    tools['qemu-system-mips64el'] = config['global']['qemu-system-mips64el'] if config['global']['qemu-system-mips64el'] is not "" else shutil.which("qemu-system-mips64el")
    tools['qemu-system-x86_64'] = config['global']['qemu-system-x86_64'] if config['global']['qemu-system-x86_64'] is not "" else shutil.which("qemu-system-x86_64")

    return tools



def writeConfig():
    global config

    # Go ahead and save case
    config.optionxform = str

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
    config['global']['qemu-system-mips64'] = ""
    config['global']['qemu-system-mips64el'] = ""
    config['global']['qemu-system-x86_64'] = ""

    writeConfig()


def writeVMConfig(env_path,tool,input_type,options):
    assert type(env_path) is str
    assert type(tool) is str
    assert type(input_type) is str
    assert type(options) is dict

    # Create config
    vm_config = configparser.ConfigParser()
    vm_config.optionxform = str 

    # Add what tool we should use
    vm_config.add_section('global')
    vm_config['global']['tool'] = tool


    # Copy in the options
    vm_config.add_section('options')
    
    for option in options:
        vm_config['options'][option] = options[option]
    
    # Set input type appropriately
    if input_type == "console":
        vm_config['options']['nographic'] = ""
        input_option = " -nographic "
    elif input_type == "curses":
        vm_config['options']['vga'] = "vmware"
        vm_config['options']['display'] = "curses"
        input_option = " -vga vmware -display curses "
    else:
        # VNC is the default display.
        input_option = ""

    with open(os.path.join(env_path,"config.ini"),"w") as f:
        vm_config.write(f)
    
    return input_option

