#!/usr/bin/env python
"""
    File: vehicle.py
    Author: Keith Gladstone

    Description:
        All operations for a Vehicle object
"""
import pixel_ops
class Vehicle(object):
    '''A vehicle will be registered in the Vehicle Log dictionary'''
    '''Construct vehicle with initial trip scheduled'''
    def __init__(self, vehicle_id,
                 latest_trip,
                 cumulative_reposition_distance,
                 most_recently_pinged_location,
                 time_of_last_ping,
                 cumulative_person_miles,
                 cumulative_vehicle_miles):
        self.latest_trip = latest_trip
        self.vehicle_id = vehicle_id
        self.most_recently_pinged_location = most_recently_pinged_location
        self.time_of_last_ping = time_of_last_ping
        self.cumulative_reposition_distance = cumulative_reposition_distance
        self.cumulative_person_miles = cumulative_person_miles
        self.cumulative_vehicle_miles = cumulative_vehicle_miles

    def add_trip_to_schedule(self, trip):
        self.latest_trip = trip.trip_id
        self.time_of_last_ping = trip.dropoff_time
        reposition_distance = float(pixel_ops.manhattan_distance(self.most_recently_pinged_location,
                                                                 trip.pickup_pixel))
        self.cumulative_reposition_distance += reposition_distance
        self.most_recently_pinged_location = trip.dropoff_pixel
        return self

    # Current policy does not allow vehicle to be interrupted while repositioning
    # Perhaps we only let it move one pixel per time iteration
    def empty_reposition(self, reposition_start_time, reposition_location):
        reposition_distance = float(pixel_ops.manhattan_distance(self.most_recently_pinged_location,
                                                                 reposition_location))
        self.cumulative_reposition_distance += reposition_distance
        reposition_duration = pixel_ops.time_of_travel(self.most_recently_pinged_location,
                                                       reposition_location)
        self.most_recently_pinged_location = reposition_location
        self.time_of_last_ping = reposition_start_time + reposition_duration
        return self


    def replace_last_trip(self, new_trip):
        self.latest_trip = new_trip.trip_id
        self.most_recently_pinged_location = new_trip.dropoff_pixel
        self.time_of_last_ping = new_trip.dropoff_time
        return self

    def __repr__(self):
        my_dict = dict()
        my_dict['latest_trip'] = self.latest_trip
        my_dict['vehicle_id'] = self.vehicle_id
        my_dict['X'], my_dict['Y'] = self.most_recently_pinged_location
        my_dict['time_of_last_ping'] = self.time_of_last_ping
        my_dict['cumulative_reposition_distance'] = self.cumulative_reposition_distance
        my_dict['cumulative_person_miles'] = self.cumulative_person_miles
        my_dict['cumulative_vehicle_miles'] = self.cumulative_vehicle_miles
        return str(my_dict)
