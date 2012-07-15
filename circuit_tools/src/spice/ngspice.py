'''
Created on 2012-07-04

@author: timvb

So far, unused... take a look deeper and see if anything useful
'''
from numpy import array, zeros
from pylab import plot, figure, grid, show, legend

import argparse
import sys

class NGSpiceData:
    """
        Class which represents ngspice simulation data
    """

    def __init__(self, filename=""):
        """
            Constructor, intializes member variables

            :Args:
                * filename (str): If filename is given it immediately loads the data from it
        """

        self.data = None
        if filename:
            self.load_data(filename)

    def load_data(self, filename):
        """
            Reads ngspice data file, generated by the ngspice 'wrdata' command,
            and puts it in a numpy array.

            :Args:
                * filename (str): The file to read

            :Returns:
                NumPy array containing the data
        """

        with open(filename) as f:
            lines = f.readlines()

            for i, line in enumerate(lines):
                parts = [float(part) for part in line.split()]

                if self.data == None:
                    self.data = zeros((len(lines), len(parts)))

                self.data[i] = array(parts)

            self.data = self.data.transpose()

    def plot(self, plot_function=plot, *legends, **kwargs):
        """
            Plots the results in a single figure

            :Args:
                * plot_function (func): The Matplotlib plot function to use
                * legends (list): Other positional arguments given to the function will be used as legends
                * Keyword arguments are forwarded to the plot function
        """

        if not 'figure' in kwargs:
            kwargs['figure'] = figure()

        i = 0

        artists = []
        while i <= len(self.data) / 2:
            artists.append(plot_function(self.data[i], self.data[i+1], **kwargs))

            i += 2

        grid(which='both')

        if legends:
            legend(artists, legends)

class PyLabAction(argparse.Action):
    """
        Retrieves a pylab function based on the argument
    """

    def __call__(self, parser, namespace, values, option_string):
        import pylab

        func = getattr(pylab, values) if hasattr(pylab, values) else pylab.plot
        setattr(namespace, self.dest, func)

if __name__ == "__main__":  
    parser = argparse.ArgumentParser(description="Plots ngspice results")
    parser.add_argument('file', type=str, nargs=1, action='store',
        help="The file with the data generated by the ngspice wrdata command")
    parser.add_argument('legend', type=str, nargs='*', default=[], 
        help="Optional legend names for the plotted lines")
    parser.add_argument('--plotfunc', '-p', type=str, dest="plot_func", default=plot,
        action=PyLabAction, help="The matplotlib (pylab) plot function to use, default pylab.plot")

    arguments = parser.parse_args(sys.argv[1:])

    results = NGSpiceData(arguments.file[0])
    results.plot(arguments.plot_func, *arguments.legend)
    show()