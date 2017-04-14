#!/usr/bin/env python
"""
    File: demand.py
    Author: Keith Gladstone
    Description:
        This file contains functions that are used
        by run_demand.py and demand_plot.py to
        plot occupancy and request rate graphs
"""
from pathlib import Path
import csv
import trip_ops
import pixel_ops
import generic_ops

def make_trip_request_schedule(trip_log, args):
    '''Create time schedule of trips requested in a given minute.'''
    start_second = 32572800
    print "Creating trip origin log indexed by minute."
    pixel_list = args['pixel_list']
    time_schedule = dict()
    for trip_id in trip_log:
        trip = trip_ops.get_trip(trip_log, trip_id)
        for pixel in pixel_list:
            if pixel_ops.same_pixel(trip.pickup_pixel, pixel):
                minute = int((trip.pickup_request_time - start_second)/ 60)
                assert minute >= 0 and minute <= 1440
                time_schedule = generic_ops.add_to_dict_of_lists(time_schedule,
                                                                 minute,
                                                                 trip.trip_id)
    return time_schedule

def sub_make_trips_in_progress_log(trip_log):
    '''Create time schedule of trips in progress in a given minute.'''
    print "Creating trip progress log indexed by minute."
    start_second = 33609600 # for the week data

    time_schedule = dict()
    for trip_id in trip_log:
        if trip_id % 1000 == 0:
            print trip_id
        trip = trip_ops.get_trip(trip_log, trip_id)
        pickup_minute = (trip.pickup_request_time - start_second) / 60
        dropoff_minute = (trip.original_dropoff_time - start_second) / 60

        if pickup_minute >= 0:
            assert pickup_minute <= dropoff_minute
            minutes_range = range(pickup_minute, dropoff_minute)
            for minute in minutes_range:
                time_schedule = generic_ops.add_to_dict_of_lists(time_schedule,
                                                                 minute,
                                                                 trip.trip_id)
    return time_schedule

def make_trips_in_progress_log(trip_log, args):
    '''Wrapper for sub_make_trips_in_progress_log.'''
    return sub_make_trips_in_progress_log(trip_log)

def memoized_time_schedule(trip_log, filename, make_function, args):
    ''' Check if generic time schedule is in cache,
        otherwise make a new one with make_function.'''
    my_file = Path(filename)
    if my_file.is_file():
        with open(filename, "rb") as inputfile:
            reader = csv.reader(inputfile)
            time_schedule = dict()
            minute = 0
            for row in reader:
                time_schedule[minute] = row
                minute += 1
    else:
        time_schedule = make_function(trip_log, args)
        with open(filename, "wb") as outfile:
            keys = sorted(time_schedule.keys())
            writer = csv.writer(outfile)
            for minute in keys:
                writer.writerow(time_schedule[minute])
    return time_schedule

def get_trip_request_schedule(trip_log, root_file, pixel, degree):
    '''Time schedule for trip requests.'''
    superpixel = pixel_ops.get_superpixel_degree_n(pixel, degree)
    pixel_str = str(pixel).replace("(", "_").replace(")", "_").replace(" ", "").replace(",", "-")
    filename = "../csv/demand_progress/" + root_file + pixel_str + "_degree" + str(degree) + ".csv"
    args = dict()
    args['pixel_list'] = superpixel
    return memoized_time_schedule(trip_log, \
        filename, make_trip_request_schedule, args)

def get_trips_in_progress_schedule(trip_log, root_file):
    '''Time schedule for trips in progress.'''
    filename = "../csv/demand_progress/" + root_file + ".csv"
    return memoized_time_schedule(trip_log, \
        filename, make_trips_in_progress_log, args=dict())

def time_schedule_to_demand_count(trip_log, time_schedule, max_minute_of_schedule):
    '''Given a time schedule of trip_IDs, sum the demand by minute.'''
    if max_minute_of_schedule is None:
        max_minute_of_schedule = max([m for m in time_schedule.keys()])
    demand_list = [0 for minute in xrange(max_minute_of_schedule)]
    for minute in xrange(max_minute_of_schedule):
        assert minute <= max_minute_of_schedule
        if minute in time_schedule.keys():
            for trip_id in time_schedule[minute]:
                trip = trip_ops.get_trip(trip_log, trip_id)
                demand_list[minute] += trip.occupancy
    return demand_list, max_minute_of_schedule

def citywide_demand_per_minute(trip_log, root_file, max_minute_of_schedule):
    '''Create a daily model of city at large.'''
    time_schedule = get_trips_in_progress_schedule(trip_log, root_file)
    return time_schedule_to_demand_count(trip_log, time_schedule, max_minute_of_schedule)

def superpixel_demand_per_minute(trip_log, root_file, pixel, degree, max_minute_of_schedule):
    '''Create a daily model of occupants requesting per minute in a superpixel.'''
    time_schedule = get_trip_request_schedule(trip_log, root_file, pixel, degree)
    print time_schedule
    return time_schedule_to_demand_count(trip_log, time_schedule, max_minute_of_schedule)

def pixel_demand_per_minute(trip_log, root_file, pixel, max_minute_of_schedule):
    '''Create a daily model of occupants requesting per minute in a pixel.'''
    return superpixel_demand_per_minute(trip_log, root_file, pixel, 0, max_minute_of_schedule)
