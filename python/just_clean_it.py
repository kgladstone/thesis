#!/usr/bin/env python
"""
    File: just_clean_it.py
    Author: Keith Gladstone
    Description:
        Quick script to just clean a raw data file
"""
import clean_trip_schedule
clean_trip_schedule.run_clean_trip_schedule("yellow_tripdata_2016-01-13")
print "Raw trips are cleaned!"
