#!/usr/bin/env python
"""
    File: pixel_ops.py
    Author: Keith Gladstone
    Description:
        Lower level pixel-related operations
"""
import sys

def latitude_to_y_coord(lat_coord):
    '''Map latitude coordinate to pixel y-coordinate'''
    shift = -40.54
    scale = 200
    y_coord = int((lat_coord + shift) * scale)
    if y_coord < 0:
        print lat_coord
        assert(False), "y is negative"
    return y_coord

def longitude_to_x_coord(long_coord):
    '''Map longitude coordinate to pixel x-coordinate'''
    shift = 74.356
    scale = 200
    x_coord = int((long_coord + shift) * scale)
    if x_coord < 0:
        print long_coord
        assert(False), "x is negative"
    return x_coord

def pixelate_pair(point):
    '''Pixelate a pair of lng, lat'''
    lng, lat = point
    return (longitude_to_x_coord(lng), latitude_to_y_coord(lat))

def pixelate_pairs(my_list):
    '''Run pixelate_pair over a list'''
    return [pixelate_pair(pair) for pair in my_list]

def pixelate_trip(pickup_pixel, dropoff_pixel):
    '''Pixelate the origin and destination of trip'''
    trip_dict = dict()
    trip_dict['pickup_pixel'] = pixelate_pair(pickup_pixel)
    trip_dict['dropoff_pixel'] = pixelate_pair(dropoff_pixel)
    return trip_dict

def same_pixel(pixel_1, pixel_2):
    return pixel_1[0] == pixel_2[0] and pixel_1[1] == pixel_2[1]

def get_superpixel_degree_n(pixel, degree):
    x_coord, y_coord = pixel
    pixel_list = list()
    for x_i in range(x_coord - degree, x_coord + degree + 1):
        for y_j in range(y_coord - degree, y_coord + degree + 1):
            if x_i > 0 and y_j > 0:
                pixel_list.append((x_i, y_j))
    return pixel_list

def get_superpixel(pixel):
    return get_superpixel_degree_n(pixel, 1)

# Get up-down even first, then do left-right
def get_one_pixel_toward(current_p, target_p):
    current_x, current_y = current_p
    target_x, target_y = target_p
    if same_pixel(current_p, target_p):
        return target_p

    if current_y == target_y:
        if current_x < target_x:
            return (current_x + 1, current_y)
        else:
            return (current_x - 1, current_y)

    elif current_y < target_y:
        return (current_x, current_y + 1)
    else:
        return (current_x, current_y - 1)

def is_pixel_in_rectangle(p, rect):
    px, py = p
    x_lo, y_lo, x_hi, y_hi = rect
    return x_lo <= px and px <= x_hi and y_lo <= py and py <= y_hi

def get_pixel_sqdistance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return (int(x2) - int(x1)) ** 2 + ((int(y2) - int(y1)) ** 2)

def manhattan_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return int(abs(x1 - x2)) + int(abs(y1 - y2))

def time_of_travel(p1, p2):
    dist = manhattan_distance(p1, p2)
    MANHATTAN_SPEED = 0.57053355301967001 # from analysis
    return dist/MANHATTAN_SPEED

def copy_of_list_without_item(l, i):
    l2 = list()
    for item in l:
        if item != i:
            l2.append(item)
    return l2

def construct_path_tree(origin, destination_list):
    if len(destination_list) == 0:
        return {origin : [(0, None)]}
    else:
        tree = {origin : list()}
        for destination in destination_list:
            remaining_destination_list = copy_of_list_without_item(destination_list, destination)
            tree[origin].append((manhattan_distance(origin[0], destination[0]),\
              (construct_path_tree(destination, remaining_destination_list))))
        return tree

def get_shortest_path_from_tree(tree):
    root, nodes = tree.items()[0]
    if len(nodes) == 1:
        distance, extra = nodes[0]
        if extra is None:
            return (0, [])
        assert(extra != None), "Extra cannot be None"
        point = extra.items()[0][0]
        path = [root, point]
        t = (distance, path)
        return t
    else:
        min_distance = sys.maxint
        for distance, node in nodes:
            cumulative_distance, path = get_shortest_path_from_tree(node)
            if distance + cumulative_distance < min_distance:
                min_distance = distance + cumulative_distance
                champion_path = path
        t = (min_distance, [root] + champion_path)
    return t

def hamilton(origin, destination_list):
    t = construct_path_tree(origin, destination_list)
    return get_shortest_path_from_tree(t)

def hamilton_of_trip_list(trip_list):
    origin = (trip_list[0].oP, trip_list[0])
    destination_list = [(trip.dP, trip) for trip in trip_list]
    return hamilton(origin, destination_list)

def test_hamilton():
    origin = (1, 1)
    destination_list = [\
      (5, 5),\
      (60, 10),\
      (2, 2),\
    ]
    result = hamilton(origin, destination_list)
    assert(str(result) == "(68, [(1, 1), (2, 2), (5, 5), (60, 10)])"), "Violates hamilton test"
    print result
