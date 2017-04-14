#!/usr/bin/env python
"""
    File: latex_post_process.py
    Author: Keith Gladstone
    Description:
        Create latex table from performance.py output
"""

import csv
from itertools import izip

def create_latex_table(filename):
    '''Create the table.'''
    headers = [
        "Number of Trip Requests",
        "Fleet Size",
        "Maximum Vehicle Capacity",
        "Departure Delay User Tolerance",
        "Frequency of Empty Repositioning",
        "Degree of Superpixel for Local Demand Survey",
        "Maximum Circuity of Ridesharing Trips",
        "Maximum Number of Intermediate Ridesharing Stops",
        "Initial Precision Beta for Demand Learning",
        "Observation Precision Beta for Demand Learning",
        "Per Occupant Waiting Time",
        "Per Trip \\newline Repositioning Distance",
        "Average Vehicle Occupancy (AVO)",
        "Average Trip Circuity"]

    data = izip(*csv.reader(open(filename, "r")))
    num_experiments = len(list(csv.reader(open(filename, "r"))))

    latex_pre = """\\begin{tabularx}{8.25in}"""
    latex_post = "\\end{tabularx}"
    column_setup = "{|p{132px}|" + ("l|"*num_experiments) + "} \\hline \n"
    header_text = "\\textbf{Experiment} & " + \
                  " & ".join(["\\textbf{" + str(k + 1) + "}" for k in range(num_experiments)]) + \
                  "\\\\ \\hline \n"
    result = latex_pre + column_setup + header_text

    for i, row in enumerate(data):
        result += "\\textbf{" + headers[i] + "} & " + " & ".join(row) + " \\\\ \\hline\n"

    result += latex_post
    return result
