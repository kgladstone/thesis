#!/usr/bin/env python
"""
    File: demand_plot.py
    Author: Keith Gladstone
    Description:
        This file contains plotting functions for demand graphs
"""

import seaborn as sns
import pylab
import numpy as np

def plot_two_vectors(source_list, x_max, title, ylab):
    ''' Plot two vectors in source_list on the same graph '''
    vector_1, vector_2 = zip(*source_list)
    demand_1 = np.asarray(vector_1)
    demand_2 = np.asarray(vector_2)
    fig = pylab.figure()
    axis_object = fig.gca()
    axis_object.set_autoscale_on(False)

    pylab.title(title)
    axis_object.axis([0, x_max, 0, 1.2 * np.max(demand_1)])
    axis_object.set_xlim(0, x_max)
    if x_max <= 1440:
        x_values = range(x_max / 8, x_max, x_max / 8)
        # pylab.xticks(x_values, [(str(i/60) + ':00') for i in x_values])
        pylab.xlabel('Minute')

    else:
        x_values = range(1440, x_max, 1440)
        pylab.xticks(x_values, [(str(i / 1440)) for i in x_values])
        pylab.xlabel('Day')

    ylab1, ylab2 = ylab
    ax1 = fig.add_subplot(111)
    lns1 = ax1.plot(demand_1, label=ylab1, color=sns.xkcd_rgb["pale red"])
    pylab.ylabel(ylab1)


    ax2 = ax1.twinx()
    lns2 = ax2.plot(demand_2, label=ylab2, color=sns.xkcd_rgb["faded green"])
    ax2.set_ylim(0, np.max(demand_2)*1.1)

    # make legend
    lns = lns1+lns2
    labs = [l.get_label() for l in lns]
    axis_object.legend(lns, labs, loc=2)
    pylab.ylabel(ylab2)

    ax1.set_yticks(np.linspace(ax1.get_ybound()[0], ax1.get_ybound()[1], 5))
    ax2.set_yticks(np.linspace(ax2.get_ybound()[0], ax2.get_ybound()[1], 5))

    pylab.show()
    return


def plot_demand(demand_list, x_max, title, ylab):
    ''' Plot single vector (time series) on a graph '''
    demand = np.asarray(demand_list)
    fig = pylab.figure()
    axis_object = fig.gca()
    axis_object.set_autoscale_on(False)

    pylab.title(title)
    axis_object.axis([0, x_max, 0, 1.2 * np.max(demand)])
    pylab.ylabel(ylab)
    if x_max <= 1440:
        x_values = range(x_max / 8, x_max, x_max / 8)
        pylab.xticks(x_values, [(str(i / 60) + ':00') for i in x_values])
        pylab.xlabel('Time')



    else:
        x_values = range(1440, x_max, 1440)
        daterange = ["1-" + str(i) + "-16" for i in range(26, 31)]
        pylab.xticks(x_values, daterange)
        pylab.xlabel('Date')

    axis_object = sns.tsplot(demand)
    pylab.show()
    return
