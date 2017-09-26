#!/usr/bin/env python3

import readline
import sys

import yt
import yt.utilities.exceptions as yt_except
import matplotlib as mpl

readline.parse_and_bind("tab: complete")
readline.parse_and_bind('set editing-mode emacs')

yt.funcs.mylog.setLevel(0)

PROMPT = "> "

COMMANDS = ["help",
            "listvar",
            "plot",
            "quit",
            "replot",
            "save",
            "set"]

# this is a global -- we will work with a single file and cache it
CURRENT_FILE = None

class FileInfo(object):
    """ cache the file info so we don't have to continually load things """

    def __init__(self, filename):
        self.name = filename.replace("\"", "").replace("'", "")
        print("trying to open: {}", self.name)
        try:
            self.ds = yt.load(self.name)
        except yt_except.YTOutputNotIdentified:
            print("file unable to be opened\n")
            raise IOError()

        self.ds.index
        self.varlist = self.ds.field_list

def listvar_cmd(pp):
    """ listvar command takes a single argument: plotfile """
    global CURRENT_FILE

    pfile = pp[0]
    if CURRENT_FILE is None or CURRENT_FILE.name != pfile:
        try:
            CURRENT_FILE = FileInfo(pfile)
        except IOError:
            return

    for f in CURRENT_FILE.varlist:
        print(f)
    print("")

def plot_cmd(pp):
    """ plot command takes 2 arguments: plotfile, variable name """
    global CURRENT_FILE

    pfile = pp[0]
    if CURRENT_FILE is None or CURRENT_FILE.name != pfile:
        try:
            CURRENT_FILE = FileInfo(pfile)
        except IOError:
            return

    slc = CURRENT_FILE.ds.slice("z")
    plt.show()

    for f in CURRENT_FILE.varlist:
        print(f)
    print("")

def main():

    print("Welcome to amrplot.  Type 'help' for a list of commands.\n")

    while True:

        cmd_str = input(PROMPT)

        if cmd_str == "":
            continue

        parts = cmd_str.split()
        command = parts[0].lower()

        # # the file is always the second part, for commands that take
        # # arguments
        # filename = parts[1]

        if command not in COMMANDS:
            print("invalid command\n")
            continue

        if command == "help":
            for c in COMMANDS:
                print(c)
            print("")

        elif command == "quit":
            sys.exit("good bye")

        else:
            fname = "{}_cmd".format(command)
            this_module = sys.modules[__name__]
            method_to_call = getattr(this_module, fname)
            method_to_call(parts[1:])

if __name__ == "__main__":
    main()
