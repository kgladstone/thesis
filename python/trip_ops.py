#!/usr/bin/env python
"""
    File: trip_ops.py
    Author: Keith Gladstone

    Description:
        All operations for a Trip object
"""

import csv
import pixel_ops

''' Trip Object '''
class Trip(object):
    def __init__(self, trip_id, pickup_pixel, dropoff_pixel,
                 pickup_request_time, original_dropoff_time, pickup_time,
                 dropoff_time, occupancy, day_of_week):
        self.trip_id = trip_id
        self.joined_trip_id = trip_id
        self.vehicle_id = trip_id
        if isinstance(pickup_pixel, str):
            x, y = pickup_pixel.replace("(", "").replace(")", "").replace(" ", "").split(",")
            self.pickup_pixel = int(x), int(y)
        else:
            self.pickup_pixel = pickup_pixel
        if isinstance(dropoff_pixel, str):
            x, y = dropoff_pixel.replace("(", "").replace(")", "").replace(" ", "").split(",")
            self.dropoff_pixel = int(x), int(y)
        else:
            self.dropoff_pixel = dropoff_pixel
        self.pickup_request_time = pickup_request_time
        self.original_dropoff_time = original_dropoff_time
        self.pickup_time = pickup_time
        self.dropoff_time = dropoff_time
        self.occupancy = occupancy
        self.day_of_week = day_of_week
        assert(not isinstance(self.pickup_pixel, str)), pickup_pixel

    def valid(self):
        if self.original_dropoff_time < self.pickup_request_time:
            assert False, \
            """
            Error: Trip Invalid
            original dropoff < pickup request
            Trip is %s
            """ % (self.__dict__)
        if self.pickup_time < self.pickup_request_time:
            assert False, \
            """
            Error: Trip Invalid
            pickup < pickup request
            Trip is %s
            """ % (self.__dict__)
        if self.occupancy == 0:
            assert False, \
            """
            Error: Trip Invalid
            occupancy 0
            Trip is %s
            """ % (self.__dict__)

        return True

    def __repr__(self):
        my_dict = dict()
        my_dict['joined_trip_id'] = self.joined_trip_id
        my_dict['trip_id'] = self.trip_id
        my_dict['vehicle_id'] = self.vehicle_id
        my_dict['oX'], my_dict['oY'] = self.pickup_pixel
        my_dict['dX'], my_dict['dY'] = self.dropoff_pixel
        my_dict['pickup_request_time'] = self.pickup_request_time
        my_dict['original_dropoff_time'] = self.original_dropoff_time
        my_dict['pickup_time'] = self.pickup_time
        my_dict['dropoff_time'] = self.dropoff_time
        my_dict['occupancy'] = self.occupancy
        my_dict['day_of_week'] = self.day_of_week
        return str(my_dict)

    def increase_time_delay(self, time_delay):
        self.pickup_time += time_delay
        self.dropoff_time += time_delay
        assert(self.valid()), "Increase Time Delay Broke It"
        return self

    def set_actual_t(self, pickup_time, dropoff_time):
        self.pickup_time = pickup_time
        self.dropoff_time = dropoff_time
        assert(self.valid()), "Set Actual Time Broke It"
        return self

    def get_time_delay(self):
        return self.pickup_time - self.pickup_request_time

    def set_vehicle(self, vehicle_id):
        self.vehicle_id = vehicle_id
        assert(self.valid()), "Set Vehicle ID Broke It"
        return self

    def same_pickup_info(self, that):
        return (self.pickup_pixel == that.pickup_pixel and
                self.pickup_time == that.pickup_time)

    def same_dropoff_pickup_info(self, that):
        return (self.pickup_pixel == that.pickup_pixel and
                self.dropoff_pixel == that.dropoff_pixel and
                self.pickup_time == that.pickup_time and
                self.dropoff_time == that.dropoff_time)

    def get_next_joined_trip_id(self):
        assert(self.trip_id != self.joined_trip_id), "No Next Ridesharing ID Exists"
        return self.joined_trip_id

def parse_pair_with_paren(pair):
    x_coord, y_coord = pair.replace(")", "").replace("(", "").replace(" ", "").split(",")
    return (int(x_coord), int(y_coord))

'''
  Args:
    trip_log:              trips schedule
    trip_ids:              identifier of a specific trip
    
  Returns:
    log

'''
def subset_trip_log(trip_log, trip_ids):
    log = [get_trip(trip_log, trip_id) for trip_id in trip_ids]
    return log

'''
  Args:
    t1, t2: trip dict
  Returns:
    (bool) if the trips are equal

  O(1) 
'''
def is_same_trip(t1, t2):
    return t1.pickup_pixel == t2.pickup_pixel and t1.dropoff_pixel == t2.dropoff_pixel

def get_trip(trip_log, trip_id):
    return trip_log[int(trip_id)]

def get_last_joined_trip(trip_log, primary_trip_id):
    trip = get_trip(trip_log, primary_trip_id)
    while trip.trip_id != trip.joined_trip_id:
        trip = get_trip(trip_log, trip.joined_trip_id)
    return trip


def get_all_joined_trips(trip_log, primary_trip_id):
    trip = get_trip(trip_log, primary_trip_id)
    l = [trip]
    while trip.trip_id != trip.joined_trip_id:
        trip = get_trip(trip_log, trip.joined_trip_id)
        l.append(trip)
    return l

def get_person_miles_of_joined_trip(trip_log, primary_trip_id):
    PM = 0
    legs = get_all_joined_trips(trip_log, primary_trip_id)
    for leg in legs:
        direct_occupancy = leg.occupancy
        direct_distance = pixel_ops.manhattan_distance(leg.pickup_pixel, leg.dropoff_pixel)
        PM += direct_occupancy * direct_distance
    return PM

def get_vehicle_miles_of_joined_trip(trip_log, primary_trip_id):
    VM = 0
    legs = get_all_joined_trips(trip_log, primary_trip_id)
    leg_start = legs[0].pickup_pixel
    for leg in legs:
        VM += pixel_ops.manhattan_distance(leg_start, leg.dropoff_pixel)
        leg_start = leg.dropoff_pixel
    return VM


def get_weighted_circuity_of_trip(trip_log, primary_trip_id):
    legs = get_all_joined_trips(trip_log, primary_trip_id)
    weighted_circuity = 0.0
    circuitous_distance = 0.0
    leg_start = legs[0].pickup_pixel
    total_occupancy = sum([leg.occupancy for leg in legs])
    assert(total_occupancy != 0), "Total Occupancy is 0" + str(legs[0])
    for leg in legs:
        direct_distance = pixel_ops.manhattan_distance(leg.pickup_pixel, leg.dropoff_pixel)
        assert(direct_distance != 0), "Trip is Zero Distance"
        circuitous_distance += pixel_ops.manhattan_distance(leg_start, leg.dropoff_pixel)
        weighted_circuity += (1.0 * (leg.occupancy * circuitous_distance) /
                              direct_distance) / total_occupancy
        leg_start = leg.dropoff_pixel

    return weighted_circuity

def is_trip_in_progress(trip_log, trip_id, time):
    trip = get_trip(trip_log, trip_id)
    return trip.pickup_time <= time and time <= trip.dropoff_time

def is_between_request_and_dropoff(trip_log, trip_id, time):
    trip = get_trip(trip_log, trip_id)
    return trip.pickup_request_time <= time and time <= trip.dropoff_time

def is_trip_complete(trip_log, trip_id, time):
    trip = get_trip(trip_log, trip_id)
    return trip.dropoff_time <= time

def process_cleaned_trip(t):
    return Trip(
        int(t['trip_id']),
        (int(t['oX']), int(t['oY'])),
        (int(t['dX']), int(t['dY'])),
        int(float(t['pickup_request_time'])),
        int(float(t['original_dropoff_time'])),
        int(float(t['pickup_request_time'])),
        int(float(t['original_dropoff_time'])),
        int(t['occupancy']),
        int(t['day_of_week'])
        )

def read_n_cleaned_trips(reader, n):
    trip_log = dict()
    k = 0
    for t in reader:
        if k == n:
            break
        trip = process_cleaned_trip(t)
        assert(trip.valid()), "Read n Cleaned Trips"
        trip_log[trip.trip_id] = trip
        k += 1
    return trip_log

def read_cleaned_trips(csv_fp):
    trip_log = dict()
    with open(csv_fp, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for t in reader:
            trip = process_cleaned_trip(t)
            assert(trip.valid()), "Read Cleaned Trips"
            trip_log[trip.trip_id] = trip
    return trip_log

def read_cleaned_vehicles(csv_fp):
    vehicles_log = dict()
    with open(csv_fp, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            vehicle = process_cleaned_trip(row)
            vehicles_log[vehicle.vehicle_id] = vehicle
    return vehicles_log

def get_trip_log(root_file):
    csv_fp = '../csv/cleaned/' + root_file + '_cleaned.csv'
    trip_log = read_cleaned_trips(csv_fp) # Trip Schedule
    return trip_log

def get_vehicle_log(root_file):
    csv_fp = '../csv/cleaned/' + root_file + '_cleaned_vehicles.csv'
    trip_log = read_cleaned_vehicles(csv_fp) # Vehicle Schedule
    return trip_log

def read_result_trips(csv_fp):
    trip_log = dict()
    with open(csv_fp, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for t in reader:
            trip = Trip(
                int(t['trip_id']),
                t['pickup_pixel'],
                t['dropoff_pixel'],
                int(float(t['pickup_request_time'])),
                int(float(t['original_dropoff_time'])),
                int(float(t['pickup_time'])),
                int(float(t['dropoff_time'])),
                int(t['occupancy']),
                int(t['day_of_week'])
                )
            assert(trip.valid()), "Read Result Trips"
            trip_log[trip.trip_id] = trip
    return trip_log

def get_results_trip_log(csv_fp):
    trip_log = read_result_trips(csv_fp) # Trip Schedule
    return trip_log

def write_trip_log(table_dict, raw, index):
    table = table_dict.values()
    keys = table[0].__dict__.keys()
    with open('../csv/results/' + raw + "_" + str(index) + "_results.csv", 'wb') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        for row in table:
            dict_writer.writerow(row.__dict__)

def write_vehicles_log(table_dict, raw, index):
    table = table_dict.values()
    keys = table[0].__dict__.keys()
    with open('../csv/results/' + raw + "_" + index + "_results_vehicles.csv", 'wb') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        for row in table:
            dict_writer.writerow(row.__dict__)

def write_dict_to_csv(t, fn, header):
    with open('../csv/' + fn, 'wb') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        for key, value in t.items():
            writer.writerow([key, value])
