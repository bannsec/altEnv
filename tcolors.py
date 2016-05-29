BLUE = '\033[94m'
GREEN = '\033[92m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def red(s):
    return RED + s + ENDC


def green(s):
    return GREEN + s + ENDC


def blue(s):
    return BLUE + s + ENDC

def underline(s):
    return UNDERLINE + s + ENDC


def bold(s):
    return BOLD + s + ENDC
