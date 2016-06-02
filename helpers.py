import shutil
import configparser
import multiprocessing
import os.path
import os

CONFIG_FILE = "config.ini"


def getVMVariables():
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

    return env_name, full_env_path, hd_size, smp, memory


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

    writeConfig()

