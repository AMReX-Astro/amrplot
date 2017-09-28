#!/usr/bin/env python3

import matplotlib as mpl
mpl.use("QT5Agg")

import matplotlib.pyplot as plt

import readline
import sys

import yt
import yt.utilities.exceptions as yt_except

# assume that our data is in CGS
from yt.units import cm

#plt.ion()
yt.toggle_interactivity()

# look at this for history persistance (using atexit):
# https://gist.github.com/thanhtphung/20980ebee86e24933b13
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
            self.is_axisymmetric = self.ds.geometry == "cylindrical"

class State(object):
    """ keep track of the current state of the plot, limits, etc"""

    def __init__(self, file_info):
        self.file_info = file_info

        self.figure = plt.figure()

        # coordinate limits
        self.xbounds = None
        self.ybounds = None
        self.zbounds = None

        # variable limits
        self.varname = None
        self.vbounds = None

        self.log = False

    def reset(self):
        # coordinate limits
        self.xbounds = None
        self.ybounds = None
        self.zbounds = None

        # variable limits
        self.varname = None
        self.vbounds = None

        self.log = False


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

    ss.varname = pp[1]

    if ss.file_info.is_axisymmetric:
        slc = yt.SlicePlot(ds, "theta", ss.varname, origin="native")
    else:
        slc = yt.SlicePlot(ds, "z", ss.varname, origin="native")

    slc.set_log(ss.varname, ss.log)
    slc.plots[ss.varname].figure = plt.gcf()
    slc.plots[ss.varname].axes = plt.gca()
    #slc._setup_plots()
    slc.show()


def set_cmd(ss, pp):
    """ set takes a property and a value """

    if pp[0] == "log":
        if pp[1].lower() in ["true", "1", "on"]:
            ss.log = True
        else:
            ss.log = False


def replot_cmd(ss, pp):
    plot_cmd(ss, [ss.file_info.name, ss.varname])


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
