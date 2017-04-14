#!/usr/bin/env python
"""
    File: demand_learning.py
    Author: Keith Gladstone
    Description:
        This file contains the Bayesian updating operations
    Notes:
        The Day column is 0 if weekday or 1 if weekend
        The Minute column is actually 30-minute blocks
        Prior beta is 1
        Num time blocks per day is 48
        Num day codes is 2
"""
import generic_ops
import trip_ops

def write_prior_file(demand_data):
    '''Writes prior belief model to csv file'''
    text = ""
    for pixel in demand_data:
        day_data = demand_data[pixel]
        for day_code in day_data:
            time_block_dict = day_data[day_code]
            for block in time_block_dict:
                value = time_block_dict[block]
                text += ",".join([str(pixel), str(day_code), str(block), str(value)]) + "\n"
    output_file = open("../csv/prior_demand/priors.csv", "w")
    output_file.write(text)
    output_file.close()

def read_prior_file():
    '''Reads in the prior beilef model from csv'''
    demand_data = dict()
    with open("../csv/prior_demand/priors.csv", "rb") as input_file:
        print "Reading demand priors" # 16,783,200
        counter = 0
        for row in input_file:
            items = row.replace(")", "").replace("(", "").\
                    replace(" ", "").replace("\n", "").split(",")
            x_coord, y_coord, \
            day_code, time_block, \
            prior_beta, demand_value = [int(item) for item in items]

            pixel = (x_coord, y_coord)
            if pixel not in demand_data:
                demand_data[pixel] = dict()
            if day_code not in demand_data[pixel]:
                demand_data[pixel][day_code] = dict()
            if time_block not in demand_data[pixel][day_code]:
                demand_data[pixel][day_code][time_block] = (demand_value, prior_beta)
            counter += 1
        print "Done reading priors"
    return demand_data


def initialize_pixel_prior(data, pickup_pixel, prior_beta):
    '''Create initial Beliefs matrix'''
    time_blocks_per_day = 48
    day_codes_per_week = 2
    data[pickup_pixel] = dict()
    # weekday = 0; weekend = 1
    for day in range(day_codes_per_week):
        data[pickup_pixel][day] = dict()
        for time_block in range(time_blocks_per_day):
            data[pickup_pixel][day][time_block] = (0, prior_beta)
    return data

def update_belief_model(trip, priors, betas):
    '''Update belief matrix with a new trip'''
    initial_beta = betas['initial'] # 10
    beta_obs = betas['obs'] # 1

    time_block = generic_ops.get_time_block_from_time(trip.pickup_request_time)
    day_code = generic_ops.get_day_code(trip.day_of_week)

    if trip.pickup_pixel not in priors.keys():
        priors = initialize_pixel_prior(priors, trip.pickup_pixel, initial_beta)

    prior_demand_value, prior_beta = priors[trip.pickup_pixel][day_code][time_block]

    observation_value = trip.occupancy

    posterior_beta = prior_beta + beta_obs

    # Bayesian Update
    posterior_demand_value = (prior_demand_value * \
                              prior_beta + \
                              observation_value*beta_obs) / posterior_beta

    priors[trip.pickup_pixel][day_code][time_block] = posterior_demand_value, posterior_beta

    return priors

def offline_demand_learning(raw_data_file_name):
    '''Run offline learning'''
    cleaned_filepath = generic_ops.cleaned_fp(raw_data_file_name)
    historial_trip_log = trip_ops.read_cleaned_trips(cleaned_filepath)

    betas = dict()
    betas['initial'] = 1
    betas['obs'] = 1

    # Create blank demand data matrix
    demand_data = dict() # Days

    # Now iterate through the trip log and get the demand...
    for trip in historial_trip_log.values():

        # For debug
        if trip.trip_id % 10000 == 0:
            print trip.trip_id

        # Add value to corresponding cell
        demand_data = update_belief_model(trip, demand_data, betas)

    write_prior_file(demand_data)
    return
