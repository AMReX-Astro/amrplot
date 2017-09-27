#!/usr/bin/env python3

import matplotlib as mpl
mpl.use("QT4Agg")

import readline
import sys

import yt
import yt.utilities.exceptions as yt_except

yt.toggle_interactivity()

readline.parse_and_bind("tab: complete")
readline.parse_and_bind('set editing-mode emacs')

yt.funcs.mylog.setLevel(0)

PROMPT = "> "

COMMANDS = ["help",
            "listvar",
            "plot",
            "quit",
            "replot",
            "reset",
            "save",
            "set"]

class FileInfo(object):
    """ cache the file info so we don't have to continually load things """

    def __init__(self):
        self.name = None
        self.varlist = None

    def load(self, filename):
        filename = filename.replace("\"", "").replace("'", "")

        # only load if it is a new file
        if filename != self.name:
            self.name = filename
            print("trying to open: {}", self.name)
            try:
                self.ds = yt.load(self.name)
            except yt_except.YTOutputNotIdentified:
                print("file unable to be opened\n")
                self.name = None
                raise IOError()

            self.ds.index
            self.varlist = self.ds.field_list

class State(object):
    """ keep track of the current state of the plot, limits, etc"""

    def __init__(self, file_info):
        self.file_info = file_info

        # coordinate limits
        self.xbounds = None
        self.ybounds = None
        self.zbounds = None

        # variable limits
        self.varname = None
        self.vbounds = None

        self.log = 0

    def reset(self):
        # coordinate limits
        self.xbounds = None
        self.ybounds = None
        self.zbounds = None

        # variable limits
        self.varname = None
        self.vbounds = None

        self.log = 0


def listvar_cmd(ss, pp):
    """ listvar command takes a single argument: plotfile """

    try:
        filename = pp[0]
    except IndexError:
        pass
    else:
        ss.file_info.load(pp[0])

    if not ss.file_info.name is None:
        for f in ss.file_info.varlist:
            print(f)


def plot_cmd(ss, pp):
    """ plot command takes 2 arguments: plotfile, variable name """

    ss.file_info.load(pp[0])
    ds = ss.file_info.ds
    slc = yt.SlicePlot(ds, "z", "density")
    slc.show()


def reset_cmd(ss, pp):
    """ reset the plot attributes """
    ss.reset()


def main():

    print("Welcome to amrplot.  Type 'help' for a list of commands.\n")

    ff = FileInfo()
    ss = State(ff)

    while True:

        cmd_str = input(PROMPT)

        if cmd_str == "":
            continue

        parts = cmd_str.split()
        command = parts[0].lower()

        # every function takes a file object, a state object, and any commands

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
            method_to_call(ss, parts[1:])
            print("")

if __name__ == "__main__":
    main()
