#!/usr/bin/env python
"""
    File: run_demand.py
    Author: Keith Gladstone

    Description:
    This file runs the demand and demand_plot modules
"""
from pathlib import Path

import demand
import demand_plot
import trip_ops
import clean_trip_schedule
from generic_ops import cleaned_fp

XMAX = 180
YMAX = 160
MINUTES_IN_DAY = 1440

# Input file
# root_file = "taxisample100k"
root_file = "yellow_tripdata_2016-01-13"

# Read in and clean the raw trip schedule, if cleaned does not exist
CLEANED_FILEPATH = cleaned_fp(root_file)
my_file = Path(CLEANED_FILEPATH)
# if True:
if my_file.is_file() is False:
    clean_trip_schedule.run_clean_trip_schedule(root_file)
    print "Raw trips are cleaned!"
else:
    print "Cleaned file exists already. Moving on..."

# Prereq: load the trip data
print "Loading Trip Log for " + root_file
trip_log = trip_ops.get_trip_log(root_file)
print "Finished Loading Trip Log (size: " + str(len(trip_log)) + ")"

# # Generate the demand data
d, x_max = demand.citywide_demand_per_minute(trip_log, root_file, MINUTES_IN_DAY)
title = "NYC Yellow Cab Vehicle Occupancy on 1/13/16"
print "Citywide Demand Grid Created for " + root_file

# Sample Usages
# Generate the demand data for a week
# d, x_max = demand.citywide_demand_per_minute(trip_log, root_file, int(MINUTES_IN_DAY*5.1))
# title = "NYC Yellow Cab Vehicle Occupancy Over Five Day Span"
# print "Citywide Demand Grid Created for " + root_file

# Penn Station
# lat = 40.750568
# lng = -73.99351899999999
# pixel = pixelate_pair((lng, lat))

# Generate pixel demand data
# d, x_max = demand.pixel_demand_per_minute(trip_log, root_file, pixel, MINUTES_IN_DAY)
# print "Demand Schedule Created for " + root_file + " pixel " + str(pixel)
# title = "Demand for NYC Yellow Cabs Picking Up in Pixel Surrounding Penn Station"

# Generate superpixel demand data
# degree = 1
# d, x_max = demand.superpixel_demand_per_minute(trip_log, root_file, pixel, degree, MINUTES_IN_DAY)
# print "Demand Schedule Created for " + root_file + " pixel " + str(pixel) + " degree " + str(degree)
# title = "Demand for NYC Yellow Cabs Picking Up in Superpixel (deg=1) Surrounding Penn Station"

# Generate 2-degree superpixel demand data
# degree = 2
# d, x_max = demand.superpixel_demand_per_minute(trip_log, root_file, pixel, degree, MINUTES_IN_DAY)
# print "Demand Schedule Created for " + root_file + " pixel " + str(pixel) + " degree " + str(degree)
# print d
# title = "Demand for NYC Yellow Cabs Picking Up in Superpixel (deg=2) Surrounding Penn Station"

# Generate 10-degree superpixel demand data
# degree = 10
# d, x_max = demand.superpixel_demand_per_minute(trip_log, root_file, pixel, degree, MINUTES_IN_DAY)
# print "Demand Schedule Created for " + root_file + " pixel " + str(pixel) + " degree " + str(degree)
# title = "Demand for NYC Yellow Cabs Picking Up in Superpixel (deg=10) Surrounding Penn Station"

# Generate plot
demand_plot.plot_demand(d, x_max, title, 'Vehicle Occupancy')
