import os
DEBUG_MODE = False # set to False to disable debugging

def debug(*args):
    if DEBUG_MODE:
        print(*args)