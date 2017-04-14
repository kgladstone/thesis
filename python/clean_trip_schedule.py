#!/usr/bin/env python
"""
    File: clean_trip_schedule.py
    Author: Keith Gladstone

    Description:
    This file cleans raw NYC yellowcab data files,
    removing some columns and transforming others
"""

import sys
import csv
from datetime import datetime
import pixel_ops
import generic_ops

def seconds_since_midnight(t_str):
    beginning_of_year = generic_ops.get_beginning_of_year()
    date_b = datetime.strptime(t_str, '%Y-%m-%d %H:%M:%S')
    date_a = datetime.strptime(beginning_of_year, '%Y-%m-%d %H:%M:%S')
    time = (date_b - date_a).total_seconds()
    return time

def day_of_week(t_str):
    # Sunday = 0
    # Monday = 1
    # Tuesday = 2, etc.
    date_b = datetime.strptime(t_str, '%Y-%m-%d %H:%M:%S')
    date_a = datetime.strptime('2000-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    days_passed = (date_b - date_a).days - 1
    return days_passed % 7

def is_raw_trip_valid(raw_trip):
    # Pure sanity
    if (raw_trip['tpep_dropoff_datetime'] == raw_trip['tpep_pickup_datetime']) \
       or raw_trip['passenger_count'] <= 0:
        return False
    # If invalid data
    elif (int(float(raw_trip['pickup_longitude'])) == 0 or
          int(float(raw_trip['pickup_latitude'])) == 0 or
          int(float(raw_trip['dropoff_longitude'])) == 0 or
          int(float(raw_trip['dropoff_latitude'])) == 0):
        return False
    # NYC cutoff
    elif (float(raw_trip['dropoff_longitude']) < -74.163208 or
          float(raw_trip['pickup_longitude']) < -74.163208 or

          float(raw_trip['dropoff_latitude']) < 40.57 or
          float(raw_trip['pickup_latitude']) < 40.57 or

          float(raw_trip['dropoff_longitude']) > -73.829498 or
          float(raw_trip['pickup_longitude']) > -73.829498
         ):
        return False
    else:
        return True

def trip_keys():
    keys = ['occupancy', 'oX', 'oY', 'dX', 'dY', \
            'pickup_request_time', 'original_dropoff_time', 'day_of_week', 'trip_id', 'vehicle_id']
    return keys

def clean_trip(raw_trip):
    if not is_raw_trip_valid(raw_trip):
        return None
    trip_dict = dict()
    pickup_pixel = (float(raw_trip['pickup_longitude']), float(raw_trip['pickup_latitude']))
    dropoff_pixel = (float(raw_trip['dropoff_longitude']), float(raw_trip['dropoff_latitude']))
    pickup_time = raw_trip['tpep_pickup_datetime']
    dropoff_time = raw_trip['tpep_dropoff_datetime']
    trip_dict['occupancy'] = raw_trip['passenger_count']

    pixel_coords = pixel_ops.pixelate_trip(pickup_pixel, dropoff_pixel)
    trip_dict['oX'], trip_dict['oY'] = pixel_coords['pickup_pixel']
    trip_dict['dX'], trip_dict['dY'] = pixel_coords['dropoff_pixel']

    trip_dict['pickup_request_time'] = seconds_since_midnight(pickup_time)
    trip_dict['original_dropoff_time'] = seconds_since_midnight(dropoff_time)
    trip_dict['day_of_week'] = day_of_week(pickup_time)

    if int(trip_dict['pickup_request_time']) > int(trip_dict['original_dropoff_time']):
        return None

    # If trip is going nowhere then return None
    if pixel_ops.manhattan_distance((int(trip_dict['oX']), int(trip_dict['oY'])), \
                                    (int(trip_dict['dX']), int(trip_dict['dY']))) == 0:
        return None

    # If trip has no occupants return None
    if int(trip_dict['occupancy']) == 0:
        return None

    return trip_dict

def serial_read_clean(input_file, output_file_writer):
    counter = 0
    reader = csv.DictReader(input_file)
    prev_departure_time = -1*(sys.maxint)-1
    for raw_trip in reader:
        cleaned_trip = clean_trip(raw_trip)
        if cleaned_trip is not None:
            if cleaned_trip['pickup_request_time'] < prev_departure_time:
                assert(False), "This trip stream is invalid. Trips are unordered."
            cleaned_trip['trip_id'] = counter
            cleaned_trip['vehicle_id'] = counter
            counter += 1
            prev_departure_time = cleaned_trip['pickup_request_time']
            # Write trip
            output_file_writer.writerow(cleaned_trip)
    return

def run_clean_trip_schedule(rawdata_filename):
    raw_filepath = '../csv/raw/' + rawdata_filename + '.csv'
    cleaned_filepath = generic_ops.cleaned_fp(rawdata_filename)
    input_file = open(raw_filepath, 'rb')
    open(cleaned_filepath, 'w').close() # reset output_file
    output_file = open(cleaned_filepath, 'wa')
    output_file_writer = csv.DictWriter(output_file, trip_keys())
    output_file_writer.writeheader()

    # Clean all data
    serial_read_clean(input_file, output_file_writer)
