import shutil
import configparser

CONFIG_FILE = "config.ini"


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

    return tools



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

