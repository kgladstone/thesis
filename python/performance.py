#!/usr/bin/env python
"""
    File: performance.py
    Author: Keith Gladstone
    Description:
        Report the performance of the simulations
"""
import csv
import numpy as np
import pixel_ops
import trip_ops
import generic_ops

# O(V)
def total_repositioning_distance_of_fleet(vehicles_log):
    total = 0
    for vehicle_id in vehicles_log:
        total += int(vehicles_log[vehicle_id].cumulative_reposition_distance)
    return total

def waiting_time(trip):
    return float(trip.pickup_time) - float(trip.pickup_request_time)

# O(T)
def cumulative_sum_of_stat(trip_log, stat):
    return np.sum([stat(trip) for trip in trip_log.values()])

# O(T)
def per_occupant_average_of_stat(trip_log, stat):
    return np.average([stat(trip) for trip in trip_log.values()], \
        weights=[trip.occupancy for trip in trip_log.values()])

# Full of holes?
def time_vector_per_occupant_sum_of_stat(trip_log, stat):
    max_time = max([trip.pickup_request_time for trip in trip_log.values()]) / 60
    min_time = min([trip.pickup_request_time for trip in trip_log.values()]) / 60

    time_schedule = [(0, 0)] * (max_time - min_time + 1)
    for trip in trip_log.values():
        time_slot = (trip.pickup_request_time / 60) - min_time
        current_x1, current_x2 = time_schedule[time_slot]
        time_schedule[time_slot] = (trip.occupancy * stat(trip) + current_x1,
                                    trip.occupancy + current_x2)
    return time_schedule

# O(T)
def get_per_occupant_waiting_time(trip_log):
    return per_occupant_average_of_stat(trip_log, waiting_time)

# Per occupant waiting time, over time
def vector_per_occupant_waiting_time(trip_log):
    return time_vector_per_occupant_sum_of_stat(trip_log, waiting_time)

# O(T)
def get_cumulative_waiting_time(trip_log):
    return cumulative_sum_of_stat(trip_log, waiting_time)

def get_number_of_trips(trip_log):
    return len(trip_log)

def distance_of_trip(trip):
    if type(trip.pickup_pixel).__name__ == "str":
        pickup_pixel = trip_ops.parse_pair_with_paren(trip.pickup_pixel)
        dropoff_pixel = trip_ops.parse_pair_with_paren(trip.dropoff_pixel)
    else:
        pickup_pixel = trip.pickup_pixel
        dropoff_pixel = trip.dropoff_pixel
    return float(pixel_ops.manhattan_distance(pickup_pixel, dropoff_pixel))

# O(T)
def get_cumulative_distance(trip_log):
    return cumulative_sum_of_stat(trip_log, distance_of_trip)


def get_person_miles_from_vehicle_log(vehicles_log):
    person_miles = 0.0
    for vehicle_id in vehicles_log:
        person_miles += vehicles_log[vehicle_id].cumulative_person_miles
    return person_miles

# Does include repositioning vehicle miles
def get_vehicle_miles_from_vehicle_log(vehicles_log):
    vehicle_miles = 0.0
    for vehicle_id in vehicles_log:
        vehicle_miles += vehicles_log[vehicle_id].cumulative_vehicle_miles
        vehicle_miles += vehicles_log[vehicle_id].cumulative_reposition_distance
    return vehicle_miles

def performance_report(vehicles_log, arg_dict):
    filename = arg_dict['fn']
    fleet_size = arg_dict['fleet_size']
    vehicle_size = arg_dict['vehicle_size']
    departure_delay = arg_dict['departure_delay']
    max_circuity = arg_dict['max_circuity']
    max_stops = arg_dict['max_stops']
    local_demand_degree = arg_dict['local_demand_degree']
    initial_beta = arg_dict['initial_beta']
    beta_obs = arg_dict['beta_obs']
    freq_levrs = arg_dict['freq_levrs']

    results_filename = generic_ops.results_fp(arg_dict['raw'], arg_dict['index'])
    trip_log = trip_ops.get_results_trip_log(results_filename)

    number_of_trips = get_number_of_trips(trip_log)
    repositioning_distance = total_repositioning_distance_of_fleet(vehicles_log)
    per_trip_repositioning_distance = 1.0 * repositioning_distance / number_of_trips
    per_occupant_waiting_time = get_per_occupant_waiting_time(trip_log)
    total_vehicle_miles = get_vehicle_miles_from_vehicle_log(vehicles_log)
    total_person_miles = get_person_miles_from_vehicle_log(vehicles_log)
    average_vehicle_occupancy = total_person_miles / total_vehicle_miles

    csv_report = [number_of_trips, \
                fleet_size, \
                vehicle_size, \
                departure_delay, \
                freq_levrs, \
                local_demand_degree, \
                max_circuity, \
                max_stops, \
                initial_beta, \
                beta_obs, \
                round(per_occupant_waiting_time, 3), \
                round(per_trip_repositioning_distance, 3), \
                round(average_vehicle_occupancy, 3), \
                ]

    # Save
    with open(filename, "a") as csvfile:
        csvwriter = csv.writer(csvfile,
                               delimiter=',',
                               quotechar='|',
                               quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(csv_report)
    return
