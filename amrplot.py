#!/usr/bin/env python3

import sys

import matplotlib as mpl
mpl.use("QT4Agg")

import matplotlib.pyplot as plt

import readline
import re
import sys

import yt
import yt.utilities.exceptions as yt_except

# assume that our data is in CGS
from yt.units import cm

if sys.version_info.major == 2:
    input = raw_input

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
        self.dim = -1

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
            if self.ds.domain_dimensions[2] == 1:
                self.dim = 2
            else:
                self.dim = 3

class State(object):
    """ keep track of the current state of the plot, limits, etc"""

    def __init__(self, file_info):
        self.file_info = file_info

        #self.figure = plt.figure()

        # coordinate limits
        self.xbounds = None
        self.ybounds = None
        self.zbounds = None

        # variable limits
        self.varname = None
        self.vbounds = None

        self.log = False

        self.current_plot_object = None

    def get_center(self):
        """ get the coordinates of the center of the plot """
        if self.xbounds is None:
            xctr = 0.5*(self.file_info.ds.domain_left_edge[0] + 
                        self.file_info.ds.domain_right_edge[0])
        else:
            xctr = 0.5*(self.xbounds[0] + self.xbounds[1])

        if self.ybounds is None:
            yctr = 0.5*(self.file_info.ds.domain_left_edge[1] + 
                        self.file_info.ds.domain_right_edge[1])
        else:
            yctr = 0.5*(self.ybounds[0] + self.ybounds[1])
        print("yctr = ", yctr)

        if self.file_info.dim == 2:
            zctr = 0.0
        else:
            if self.zbounds is None:
                zctr = 0.5*(self.file_info.ds.domain_left_edge[2] + 
                            self.file_info.ds.domain_right_edge[2])
            else:
                zctr = 0.5*(self.zbounds[0] + self.zbounds[1])

        return (xctr, yctr, zctr)

    def get_width(self):
        """ get the width of the plot """
        if self.xbounds is None:
            xwidth = (self.file_info.ds.domain_right_edge[0] -
                      self.file_info.ds.domain_left_edge[0])
        else:
            xwidth = (self.xbounds[1] - self.xbounds[0])*cm

        if self.ybounds is None:
            ywidth = (self.file_info.ds.domain_right_edge[1] -
                      self.file_info.ds.domain_left_edge[1])
        else:
            ywidth = (self.ybounds[1] - self.ybounds[0])*cm

        if self.file_info.dim == 2:
            zwidth = 0.0
        else:
            if self.zbounds is None:
                zwidth = (self.file_info.ds.domain_right_edge[2] -
                          self.file_info.ds.domain_left_edge[2])
            else:
                zwidth = (self.zbounds[1] - self.zbounds[0])*cm

        return (xwidth, ywidth, zwidth)


    def reset(self):
        # coordinate limits
        self.xbounds = None
        self.ybounds = None
        self.zbounds = None

        # variable limits
        self.varname = None
        self.vbounds = None

        self.log = False

        self.current_plot_object = None


def listvar_cmd(ss, pp):
    """ listvar command takes a single argument: plotfile """

    try:
        filename = pp[0]
    except IndexError:
        pass
    else:
        ss.file_info.load(filename)

    if not ss.file_info.name is None:
        for f in ss.file_info.varlist:
            print(f)


def plot_cmd(ss, pp):
    """ plot command takes 2 arguments: plotfile, variable name """

    plt.clf()

    ss.file_info.load(pp[0])
    ds = ss.file_info.ds

    var = pp[1]
    if var.startswith("'") and var.endswith("'") or var.startswith('"') and var.endswith('"'):
        var = var[1:-1]

    if var in ss.file_info.ds.fields.gas or ('boxlib', var) in ds.field_list:
        ss.varname = var
    else:
        print("invalid variable")
        return

    center = ss.get_center()
    width = ss.get_width()

    if ss.file_info.is_axisymmetric:
        slc = yt.SlicePlot(ds, "theta", ss.varname, origin="native",
                           center=center, width=[width[0], width[1], width[2]])
    else:
        slc = yt.SlicePlot(ds, "z", ss.varname, origin="native",
                           center=center, width=width)

    slc.set_log(ss.varname, ss.log)
    #slc.plots[ss.varname].figure = plt.gcf()
    #slc.plots[ss.varname].axes = plt.gca()
    #slc.plots[ss.varname].cax =
    #slc._setup_plots()
    slc.show()

    ss.current_plot_obj = slc


def save_cmd(ss, pp):
    """ takes 1 argument: filename"""

    try:
        ofile = pp[0]
    except IndexError:
        print("no output file specified")
    else:
        ofile.replace("'","").replace("\"","")

    ss.current_plot_obj.save(ofile)


def set_cmd(ss, pp):
    """ set takes a property and a value """

    if pp[0] == "log":
        if pp[1].lower() in ["true", "1", "on"]:
            ss.log = True
        else:
            ss.log = False

    elif pp[0].lower() in ["xlim", "xrange", "ylim", "yrange"]:
        is_x = False
        is_y = False
        is_z = False

        if pp[0].lower().startswith("x"):
            is_x = True
        elif pp[0].lower().startswith("y"):
            is_y = True
        elif pp[0].lower().startswith("z"):
            is_z = True

        try:
            nlim_str = " ".join(pp[1:])
        except IndexError:
            print("you need to specify a range")
            return

        nlim_str = nlim_str.replace("(","").replace(")","").replace("[","").replace("]","")
        try:
            # handle multiple delimitors -- from stack overflow
            nmin, nmax = list(filter(None, re.split("[, ;]+", nlim_str)))
        except ValueError:
            print("invalid range specified")
            return

        if is_x:
            ss.xbounds = (float(nmin), float(nmax))
        elif is_y:
            ss.ybounds = (float(nmin), float(nmax))
        elif is_z:
            ss.zbounds = (float(nmin), float(nmax))

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
