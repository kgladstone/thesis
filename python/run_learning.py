#!/usr/bin/env python
"""
    File: run_learning.py
    Author: Keith Gladstone

    Description:
    This file runs the learning experiments
"""

import csv
import os
import time
from pathlib import Path
from multiprocessing import Pool
import operator

import clean_trip_schedule
import performance
import handler
import generic_ops
import demand_learning
import latex_post_process

# Run experiment
def run_experiment(arg_dict):
    print "Running Experiment #%s" % (str(arg_dict['index']))
    print "Fleet Size: %s" % (str(arg_dict['fleet_size']))
    try:
        vehicles_log = handler.handle_all_trip_requests(arg_dict)
        print "Finished Experiment #%s" % (str(arg_dict['index']))
        performance.performance_report(vehicles_log, arg_dict)
        print "Finished Performance Analysis #%s" % (str(arg_dict['index']))

    except:
        print "It broke..."
        my_list = list()
        for key, item in arg_dict.iteritems():
            if key != 'priors':
                my_list.append((key, item))
        print my_list
        raise

def main(raw_data_file_name):
    cleaned_filepath = generic_ops.cleaned_fp(raw_data_file_name)

    assert raw_data_file_name != "", "Must be a raw data file"

    time_series = time.asctime().replace(" ", "").replace(":", "")
    filename = "out/out-" + raw_data_file_name + "-" + time_series + ".csv"

    # Reset the out file
    try:
        os.remove(filename)
    except OSError:
        pass

    print "=========================================="
    print "Running trip schedule script"

    print "--------------"
    print "Raw data file: " + raw_data_file_name + ".csv"

    # Read in and clean the raw trip schedule, if cleaned does not exist
    my_file = Path(cleaned_filepath)
    if my_file.is_file() is False:
        clean_trip_schedule.run_clean_trip_schedule(raw_data_file_name)
        print "Raw trips are cleaned!"
    else:
        print "Cleaned file exists already. Moving on..."

    print "Outfile: " + filename

    # Set the parameters
    fleet_size_list = [15000]

    departure_delay_list = [60]
    max_circuity_list = [1.5]
    vehicle_size_list = [8]
    max_stops_list = [5]

    # Irrelevant until Round D
    local_demand_degree_list = [20]
    greedy_common_origin_list = [True]
    initial_beta_list = [1]
    beta_obs_list = [1]
    freq_levrs_list = [0, 900, 1800]

    prior_demand_beliefs = demand_learning.read_prior_file()

    list_of_arg_dicts = list()
    index = 0
    for departure_delay in departure_delay_list:
        for fleet_size in fleet_size_list:
            for max_circuity in max_circuity_list:
                for vehicle_size in vehicle_size_list:
                    for max_stops in max_stops_list:
                        for local_demand_degree in local_demand_degree_list:
                            for greedy_common_origin in greedy_common_origin_list:
                                for initial_beta in initial_beta_list:
                                    for beta_obs in beta_obs_list:
                                        for freq_levrs in freq_levrs_list:
                                            list_of_arg_dicts.append({\
                                                'index' : index, \
                                                'raw' : raw_data_file_name, \
                                                'fn': filename, \
                                                'priors' : prior_demand_beliefs, \
                                                'initial_beta' : initial_beta, \
                                                'beta_obs' : beta_obs, \
                                                'local_demand_degree': local_demand_degree, \
                                                'greedy_common_origin': greedy_common_origin, \
                                                'max_circuity' : max_circuity, \
                                                'max_stops' : max_stops, \
                                                'fleet_size': fleet_size, \
                                                'vehicle_size': vehicle_size, \
                                                'freq_levrs': freq_levrs, \
                                                'departure_delay': departure_delay})
                                            index += 1

    # Configure pooling [on/off]
    do_pool = False
    do_pool = True

    print "Running %s experiments..." % (len(list_of_arg_dicts))

    # Parallel
    if do_pool:
        print "In Parallel"
        pool = Pool()
        pool.map(run_experiment, list_of_arg_dicts)

    # Series
    else:
        print "In Series"
        for i in list_of_arg_dicts:
            run_experiment(i)

    # Print results
    data = csv.reader(open(filename), delimiter=',')
    sortedlist = sorted(data, key=operator.itemgetter(0, 1, 2, 3, 4))
    print "----------\nExperiment Results: "
    for row in sortedlist:
        print row


    # Latex post-processing
    print "----------\nLatex Table:"
    print "Copy and paste this latex table directly into the Thesis latex file...\n"
    print latex_post_process.create_latex_table(filename)


# Sample Executions
# main("yellow_tripdata_2016-01-week")
main("yellow_tripdata_2016-01-13")
# main("yellow_tripdata_2016-01")
