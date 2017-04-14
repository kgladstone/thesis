#!/usr/bin/env python
"""
    File: generic_ops.py
    Author: Keith Gladstone
    Description:
        This file contains generic operations
"""
from collections import deque

def get_beginning_of_year():
    '''WARNING:
        If changed, the variable "beginning_of_year_day_of_week" in
        the function "get_day_of_week_from_time" must also be changed'''
    beginning_of_year = '2015-01-01 00:00:00'
    return beginning_of_year

def get_day_of_week_from_time(time):
    '''ASSUME THAT beginning_of_year = '2015-01-01 00:00:00', which is a thursday
        WARNING:
            If changed, the variable "beginning_of_year" in
            the function "get_beginning_of_year" must also be changed'''
    beginning_of_year_day_of_week = 4
    days_since_beginning = time / 86400
    day_of_week = (days_since_beginning + beginning_of_year_day_of_week) % 7
    return day_of_week

def get_day_code(day):
    '''Maps weekday to a binary (weekday = 0, weekend = 1).'''
    if day >= 1 and day <= 5:
        day_code = 0
    else:
        day_code = 1
    return day_code

def get_time_block_from_time(time):
    '''Maps time (seconds) to half-hour block.'''
    return ((time % 86400) / 60) / 30

def list_has_duplicates(your_list):
    '''Return true if list has duplicate items.'''
    return len(your_list) != len(set(your_list))

def deque_insert(deque_instance, index, element):
    '''Insert element at index in deque_instance.'''
    deque_instance.rotate(-index)
    deque_instance.appendleft(element)
    deque_instance.rotate(index)
    return deque_instance

def deque_put_in_place(deque_instance, pair):
    '''Assume the keys are increasing
        Add to a deque to maintain increasing key order'''
    pair_key = pair[1]
    champion = 0
    for index, deque_instance_pair in enumerate(deque_instance):
        deque_instance_key = deque_instance_pair[1]
        if deque_instance_key >= pair_key:
            champion = index
            break
        if deque_instance_key < pair_key:
            champion = index + 1

    # If it reaches the end of the deq
    deque_insert(deque_instance, champion, pair)
    return deque_instance

def test_putinplace():
    '''Test "deque_put_in_place"'''
    deque_instance = deque()
    deque_instance.append(("a", 1))
    deque_instance.append(("b", 1))
    deque_instance.append(("c", 2))
    deque_instance.append(("d", 3))
    deque_instance.append(("e", 4))
    deque_instance.append(("f", 5))
    deque_instance = deque_put_in_place(deque_instance, ("testing", 4.1))
    deque_instance = deque_put_in_place(deque_instance, ("testing", 6.1))
    deque_instance = deque_put_in_place(deque_instance, ("testing", 2.1))
    deque_instance = deque_put_in_place(deque_instance, ("testing", 8.1))
    deque_instance = deque_put_in_place(deque_instance, ("testing", 1.1))
    print deque_instance
    return

def deque_index(deque_instance, item):
    '''Get index of element in deque.'''
    for k, element in enumerate(deque_instance):
        if element == item:
            return k
    return -1

def deque_replace(deque_instance, old, new):
    '''Replace "old" element with "new" element if "old" is in deque.'''
    index = deque_index(deque_instance, old)
    if index == -1:
        return deque_instance
    deque_instance.rotate(-index)
    deque_instance.popleft()
    deque_instance.appendleft(new)
    deque_instance.rotate(index)
    return deque_instance

def add_to_dict_of_lists(dictionary, key, value):
    '''Append a value to a list accessed in the hash table by a key'''
    if key not in dictionary.keys():
        dictionary[key] = list()
    dictionary[key].append(value)
    return dictionary

def list_from_dict(my_dict):
    '''Convert a dict into a list of key value pairs.'''
    my_list = list()
    for k, v in my_dict.iteritems():
        tmp = [k, v]
        my_list.append(tmp)
    return my_list

def list_replace(my_list, old, new):
    '''Replace a list element with a new element
       Behaves like a "string replace" method'''
    index = my_list.index(old)
    my_list[index] = new
    return my_list

def results_fp(raw_data_file_name, index):
    '''Get the default results filename'''
    return '../csv/results/' + raw_data_file_name + str(index) + "_results.csv"

def cleaned_fp(raw_data_file_name):
    '''Get the default cleaned data filename'''
    return "../csv/cleaned/" + raw_data_file_name + "_cleanemy_dict.csv"
