import os

PROGRAM_NAME = "pyPlanner"
AUTHOR_NAME = "Roy"
REGISTRY_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"

SIMPLE_KEY = '_d9331u189142125710_'

def generateID():
    id = SIMPLE_KEY + PROGRAM_NAME + '_' #unicode(sys.argv[0]) + '_'
    username = os.getenv('USERNAME') #Windows only
    if username: id += username
    return id 