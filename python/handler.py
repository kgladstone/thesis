#!/usr/bin/env python
"""
    Filename: handler.py
    Author: Keith Gladstone

    Description:
    This file is the heart of the program
    It handles all vehicle allocation and repositioning
    Contains trip_buffer, trip_location_hash_table, etc.
"""
import csv
import sys
from collections import deque
from math import floor

from vehicle import Vehicle
import trip_ops
import generic_ops
import pixel_ops
import demand_learning

def local_demand_predictor(current_p, day, time_block, beliefs, local_demand_degree):
    '''Determines optimal cardinal direction to move vehicle.'''
    current_x, current_y = current_p
    directional_demand = [0, 0, 0, 0] # right, up, left, down
    target_pixel = [(current_x + 1, current_y),
                    (current_x, current_y + 1),
                    (current_x - 1, current_y),
                    (current_x, current_y - 1)]
    superpixel = pixel_ops.get_superpixel_degree_n(current_p, local_demand_degree)

    for city_pixel, pixel_demand in beliefs.iteritems():
        if city_pixel in superpixel:
            (pixel_x, pixel_y) = city_pixel
            demand_value = pixel_demand[generic_ops.get_day_code(day)][time_block][0]
            if pixel_x > current_x:
                directional_demand[0] += demand_value
            if pixel_y > current_y:
                directional_demand[1] += demand_value
            if pixel_x < current_x:
                directional_demand[2] += demand_value
            if pixel_y < current_y:
                directional_demand[3] += demand_value
    return target_pixel[max((v, i) for i, v in enumerate(directional_demand))[1]]

def handle_empty_repositioning(vehicles_log, time, beliefs, local_demand_degree):
    '''Moves vehicle using LEVRS.'''
    time_block = generic_ops.get_time_block_from_time(time)
    day_of_week = generic_ops.get_day_of_week_from_time(time)

    empty_vehicles = list()
    for vehicle_id in vehicles_log:
        vehicle = vehicles_log[vehicle_id]
        last_pinged_time = vehicle.time_of_last_ping
        if last_pinged_time < time:
            empty_vehicles.append(vehicle)
    if len(empty_vehicles) == 0:
        return vehicles_log
    for empty_vehicle in empty_vehicles:
        current_loc = empty_vehicle.most_recently_pinged_location
        incremental_reposition = local_demand_predictor(\
            current_loc, day_of_week, time_block, beliefs, local_demand_degree)
        vehicles_log[empty_vehicle.vehicle_id] = \
            empty_vehicle.empty_reposition(time, incremental_reposition)
    return vehicles_log

def initial_vehicle_log(trip_log, fleet_size):
    '''Create the initial vehicles_log.'''
    list_trip_log = generic_ops.list_from_dict(trip_log)
    first_n_trips = list_trip_log[:fleet_size]
    vehicles_log = dict()
    vehicle_id = 0
    for trip_id, trip in first_n_trips:
        cumulative_person_miles = trip_ops.get_person_miles_of_joined_trip(trip_log, trip_id)
        cumulative_vehicle_miles = trip_ops.get_vehicle_miles_of_joined_trip(trip_log, trip_id)
        vehicle = Vehicle(\
            vehicle_id,
            [trip.trip_id],
            0,
            trip.dropoff_pixel,
            trip.dropoff_time,
            cumulative_person_miles,
            cumulative_vehicle_miles\
        )
        vehicles_log[vehicle_id] = vehicle
        vehicle_id += 1
    return vehicles_log

def find_best_common_origin_seq(trip_list, max_circuity, max_stops):
    '''Given a list of trips, find the best rideshared route.'''
    path = pixel_ops.hamilton_of_trip_list(trip_list)[1]
    distinct_stops = dict()

    origin_pixel = path[0][0]
    prev_destination = origin_pixel
    circuity_distance = 0
    # Check if every trip in path meets the max circuity constraint and max stops constraint
    # If constraints are met then this should NOT return None
    for pair in path[1:]:
        destination_pixel = pair[0]
        distinct_stops[destination_pixel] = True
        if len(distinct_stops) > max_stops:
            return None
        direct_manhattan_distance = pixel_ops.manhattan_distance(origin_pixel, destination_pixel)
        circuity_distance += pixel_ops.manhattan_distance(prev_destination, destination_pixel)
        prev_destination = destination_pixel
        if direct_manhattan_distance != 0:
            ratio = 1.0 * circuity_distance / direct_manhattan_distance
            if ratio > max_circuity:
                return None

    return path[1:]

def predispatched_trips(trip_log, trip_location_hash_table, pickup_pixel):
    '''Get the predispatched trips from a certain pickup_pixel.'''
    trip = list(trip_location_hash_table[pickup_pixel])[-1][1]
    return trip_ops.get_all_joined_trips(trip_log, trip.trip_id)

def optimal_route(trip, trip_log, trip_location_hash_table,
                  pickup_pixel, constraints):
    '''Get the optimal route of rideshared trips'''
    optimal_preorder = predispatched_trips( \
        trip_log, trip_location_hash_table, pickup_pixel)
    optimal_preorder += [trip]
    optimal_order = find_best_common_origin_seq(optimal_preorder,
                                                constraints['max_circuity'],
                                                constraints['max_stops'])
    return optimal_order

def sync_joined_trips(trip_log, trip_id, dispatch_time):
    '''Sync the data for rideshared trips.'''
    trip = trip_ops.get_trip(trip_log, trip_id)
    vehicle_id = trip.vehicle_id
    joined_trip_id = trip.joined_trip_id
    pickup_location = trip.pickup_pixel

    trip.pickup_time = dispatch_time

    time_elapsed = pixel_ops.time_of_travel(pickup_location, trip.dropoff_pixel)
    trip.dropoff_time = dispatch_time + time_elapsed

    # For each subsequent trip, update the time elapsed to reach destination
    # Update the vehicle id
    while True:
        joined_trip = trip_ops.get_trip(trip_log, joined_trip_id)
        time_elapsed += pixel_ops.time_of_travel(trip.dropoff_pixel, joined_trip.dropoff_pixel)
        joined_trip = joined_trip.set_actual_t(dispatch_time, dispatch_time + time_elapsed)
        joined_trip = joined_trip.set_vehicle(vehicle_id)
        trip_id = joined_trip_id
        joined_trip_id = joined_trip.joined_trip_id

        if joined_trip_id == trip_id:
            break

    return trip_log

def send_vehicle_for_this_request(trip_log, trip_id, vehicle_info, vehicles_log, constraints):
    '''Assign vehicle to trip request.'''
    departure_delay = constraints['departure_delay']
    assert(vehicle_info is not None), "Vehicle Info is None"

    vehicle_id = vehicle_info['vehicle_id']
    time_delay = vehicle_info['time_delay']

    # Update vehicle ID
    trip = trip_ops.get_trip(trip_log, trip_id)
    trip.vehicle_id = vehicle_id

    # Update trip's time delay
    trip = trip.increase_time_delay(max(time_delay, departure_delay))

    # Update trip log
    trip_log[trip_id] = trip

    # Update vehicle log accordingly
    vehicles_log[vehicle_id].add_trip_to_schedule(trip)  # this causes absurd scale

    return trip_log, vehicles_log

def get_vehicles_latest_trips(vehicles_log):
    '''Get the latest scheduled location and time of all vehicles.'''
    vehicle_locations = dict()
    for vehicle in vehicles_log.values():
        vehicle_locations[vehicle.vehicle_id] = \
            (vehicle.most_recently_pinged_location, vehicle.time_of_last_ping)
    return vehicle_locations

def vehicle_min_arrival_time(trip_log, trip_id, vehicles_log):
    '''Get the vehicle that will arrive soonest for trip_id.'''
    vehicles_latest_trips = get_vehicles_latest_trips(vehicles_log)
    trip = trip_ops.get_trip(trip_log, trip_id)
    request_time = trip.pickup_request_time

    # Get the vehicle that can arrive soonest (with travel estimate)
    closest_vehicle_info = None
    min_time = sys.maxint
    for vehicle_id, (pre_repositioned_location, pre_repositioned_time) \
        in vehicles_latest_trips.items():
        travel_time = pixel_ops.time_of_travel(pre_repositioned_location, trip.pickup_pixel)

        # Vehicle is already there, use it
        if travel_time == 0.0:
            return (vehicle_id, pre_repositioned_location, 0.0)

        time_vehicle_would_arrive = \
            max(pre_repositioned_time, request_time) + travel_time
        if time_vehicle_would_arrive < min_time:
            min_time = time_vehicle_would_arrive
            time_delay = time_vehicle_would_arrive - request_time
            assert(time_delay >= 0), \
                """
                Time Delay is negative: %s
                Trip: %s
                Pre Repositioned Time: %s
                Pre Repositioned Location: %s
                Request Time: %s
                Travel Time: %s
                Time Vehicle Would Arrive Here: %s
                """ % (str(time_delay),
                       str(trip.__dict__),
                       str(pre_repositioned_time),
                       str(pre_repositioned_location),
                       str(request_time),
                       str(travel_time),
                       str(time_vehicle_would_arrive))

            closest_vehicle_info = {"vehicle_id" : vehicle_id,
                                    "pre_repositioned_location" : pre_repositioned_location,
                                    "time_delay" : time_delay}
    assert(min_time != sys.maxint), "Closest Vehicle not selected"
    return closest_vehicle_info

def get_vehicle_for_this_trip(trip_log, trip_id, vehicles_log):
    '''Get the vehicle to be assigned for this trip.'''
    vehicle = vehicle_min_arrival_time(trip_log, trip_id, vehicles_log)
    return vehicle

def do_request_new_vehicle(trip_log, trip_id, vehicles_log,
                           constraints, trip_buffer, trip_location_hash_table):
    '''Request a new vehicle for this trip, handle info'''
    # Helper variables
    trip = trip_ops.get_trip(trip_log, trip_id)
    pickup_pixel, dropoff_pixel = (trip.pickup_pixel, trip.dropoff_pixel)

    # Need to a request a new vehicle for this trip
    #   (1) Identify which vehicle is needed
    #   (2) Update data structures to link this trip request to that vehicle and "send vehicle"
    vehicle_for_this_trip = get_vehicle_for_this_trip(trip_log, trip_id, vehicles_log)
    trip_log, vehicles_log = send_vehicle_for_this_request(trip_log, trip_id,
                                                           vehicle_for_this_trip,
                                                           vehicles_log, constraints)

    # We want to put this trip, therefore, in the trip fulfillment queue and location dict
    trip_buffer = generic_ops.deque_put_in_place(trip_buffer, (trip, trip.pickup_time))
    trip_location_hash_table[pickup_pixel].append((dropoff_pixel, trip))

    return trip_log, vehicles_log

def is_this_vehicles_latest_loc(trip_log, vehicles_log,
                                trip_location_hash_table, pickup_pixel):
    '''Is the vehicle's latest scheduled trip the latest trip scheduled at this pickup pixel?'''
    if len(trip_location_hash_table[pickup_pixel]) == 0:
        return False
    the_trip_scheduled_from_this_origin = trip_location_hash_table[pickup_pixel][-1]
    trip = the_trip_scheduled_from_this_origin[1]
    last_common_origin_trip = trip_ops.get_last_joined_trip(trip_log, trip.trip_id)
    vehicle_id = last_common_origin_trip.vehicle_id
    the_latest_trip_scheduled_with_this_vehicle = vehicles_log[vehicle_id].latest_trip
    return str(the_latest_trip_scheduled_with_this_vehicle) == str(trip.trip_id)

def get_joined_trip_occupants(trip_legs):
    '''Get the number of total occupants for all trip legs of a rideshared trip'''
    total = 0
    for trip_leg in trip_legs:
        total += trip_leg.occupancy
    return total

def common_origin_validation(trip_location_hash_table, trip_log,
                             vehicles_log, new_trip_request, constraints):
    '''Run the common origin validation process'''
    vehicle_size = constraints['vehicle_size']
    request_new_vehicle = True
    optimal_order = None

    pickup_pixel = new_trip_request.pickup_pixel

    there_exists_undispatched_vehicle_from_this_origin = \
        len(trip_location_hash_table[pickup_pixel]) > 0

    # If there exists a vehicle from this origin
    if there_exists_undispatched_vehicle_from_this_origin:

        # This is the Greedy Common Origin Trip Sender
        # If the vehicle's latest undispatched trip is not from this origin,
        #   then request a new vehicle
        if not is_this_vehicles_latest_loc(trip_log,
                                           vehicles_log,
                                           trip_location_hash_table,
                                           pickup_pixel):
            request_new_vehicle = True

        else:
            # Get pickup time of the trip
            first_leg_of_trip_here = list(trip_location_hash_table[pickup_pixel])[0][1]
            if new_trip_request.pickup_request_time > first_leg_of_trip_here.pickup_time:
                request_new_vehicle = True
            else:
                # SUBJECT TO vehicle_size CONSTRAINT
                current_joined_trip = [that_trip[1] \
                                        for that_trip \
                                        in list(trip_location_hash_table[pickup_pixel])]

                current_vehicle_occupancy = get_joined_trip_occupants(current_joined_trip)

                vehicle_would_exceed_capacity = \
                    current_vehicle_occupancy + new_trip_request.occupancy > vehicle_size

                if vehicle_would_exceed_capacity:
                    request_new_vehicle = True
                else:
                    # SUBJECT TO MAX CIRCUITY AND MAX STOPS CONSTRAINTS
                    optimal_order = optimal_route(new_trip_request,
                                                  trip_log,
                                                  trip_location_hash_table,
                                                  pickup_pixel,
                                                  constraints)
                    request_new_vehicle = optimal_order is None

    return request_new_vehicle, optimal_order

def resequence_joined_trip_ids(trip_log, ordered_joined_trips):
    '''Resync joined trip ids'''
    for i in range(0, len(ordered_joined_trips) - 1):
        trip = ordered_joined_trips[i]
        trip.joined_trip_id = ordered_joined_trips[i + 1].trip_id
    last_trip = ordered_joined_trips[-1]
    last_trip.joined_trip_id = last_trip.trip_id
    return trip_log

def greedy_common_origin_scheduler(trip_log, vehicles_log, trip_location_hash_table,
                                   trip_buffer, new_trip_request, optimal_order):
    '''Run Greedy Common Origin Strategy heuristic'''
    pickup_pixel = new_trip_request.pickup_pixel
    optimal_order_CO_destinations = [trip[1] for trip in optimal_order]
    new_first_trip_of_route = optimal_order_CO_destinations[0]
    scheduled_trip_from_this_origin = list(trip_location_hash_table[pickup_pixel])[-1][1]
    pickup_time = scheduled_trip_from_this_origin.pickup_time
    vehicle_id = scheduled_trip_from_this_origin.vehicle_id

    trip_log = resequence_joined_trip_ids(trip_log, optimal_order_CO_destinations)

    vehicles_log[vehicle_id] = \
        vehicles_log[vehicle_id].replace_last_trip(new_first_trip_of_route)
    new_trip_request.set_vehicle(vehicle_id)

    sync_joined_trips(trip_log, new_first_trip_of_route.trip_id, pickup_time)
    generic_ops.deque_replace(trip_buffer,
                              (scheduled_trip_from_this_origin, pickup_time),
                              (new_first_trip_of_route, pickup_time))
    trip_location_hash_table[pickup_pixel].popleft()
    trip_location_hash_table[pickup_pixel].append((optimal_order[0][0], new_first_trip_of_route))
    return trip_log, vehicles_log, trip_location_hash_table

def process_request(trip_log, trip, vehicles_log,
                    constraints, trip_location_hash_table, trip_buffer):
    '''Run the general process for a single trip request'''
    greedy = constraints['greedy_common_origin']
    request_new_vehicle = True # default true, but turn false if vehicle is available

    # Helper variables
    new_trip_request = trip
    pickup_pixel = new_trip_request.pickup_pixel

    # If the origin point has NOT been accounted for yet then set it up as
    # an empty deque of destination points
    if pickup_pixel not in trip_location_hash_table.keys():
        trip_location_hash_table[pickup_pixel] = deque()

    # Determine whether to request new vehicle or not
    request_new_vehicle, optimal_order = common_origin_validation(\
        trip_location_hash_table, trip_log, vehicles_log, new_trip_request, constraints)

    # HACK: to make sure that pickup_request time is not after pickup time
    if optimal_order is not None:
        pickup_pixel = new_trip_request.pickup_pixel
        new_first_trip_of_route = optimal_order[0][1]
        scheduled_trip_from_this_origin = list(trip_location_hash_table[pickup_pixel])[-1][1]
        pickup_time = scheduled_trip_from_this_origin.pickup_time
        if new_first_trip_of_route.pickup_request_time > pickup_time:
            request_new_vehicle = True

    # Request a vehicle from the fleet
    if request_new_vehicle:
        trip_log, vehicles_log = \
            do_request_new_vehicle(trip_log,
                                   trip.trip_id,
                                   vehicles_log,
                                   constraints,
                                   trip_buffer,
                                   trip_location_hash_table)

    # Enter RIDESHARE process
    # Greedy Heuristic
    else:
        if greedy:
            trip_log, vehicles_log, trip_location_hash_table = \
                greedy_common_origin_scheduler(trip_log,
                                               vehicles_log,
                                               trip_location_hash_table,
                                               trip_buffer,
                                               new_trip_request,
                                               optimal_order)
    return trip_log, vehicles_log

def handle_requests_at_this_time(trip_log, vehicles_log,
                                 requests, constraints,
                                 trip_location_hash_table, trip_buffer, beliefs):
    '''Run the processes for all requests in this batch'''
    list_of_trip_requests_now = requests
    for trip in list_of_trip_requests_now:
        trip_log[trip.trip_id] = trip
        trip_log, vehicles_log = process_request(trip_log,
                                                 trip,
                                                 vehicles_log,
                                                 constraints,
                                                 trip_location_hash_table,
                                                 trip_buffer)
        if int(constraints['freq_levrs']) != 0:
            betas = {'initial' : constraints['initial_beta'], 'obs' : constraints['beta_obs']}
            beliefs = demand_learning.update_belief_model(trip, beliefs, betas)

    return trip_log, vehicles_log, beliefs

def clear_trips_for_dispatch(trip_log, dispatch_time, vehicles_log,
                             trip_location_hash_table,
                             trip_buffer, dict_writer):
    '''Send dispatched files to output, remove from data structures'''
    if len(trip_buffer) < 1:
        return trip_location_hash_table, trip_buffer

    while len(trip_buffer) > 0:
        next_to_dispatch_trip, next_to_dispatch_pickup_time = trip_buffer[0]
        if floor(next_to_dispatch_pickup_time) <= floor(dispatch_time):
            pickup_pixel = next_to_dispatch_trip.pickup_pixel
            vehicle_id = next_to_dispatch_trip.vehicle_id
            vehicles_log[vehicle_id].cumulative_person_miles += \
                trip_ops.get_person_miles_of_joined_trip(trip_log, next_to_dispatch_trip.trip_id)
            vehicles_log[vehicle_id].cumulative_vehicle_miles += \
                trip_ops.get_vehicle_miles_of_joined_trip(trip_log, next_to_dispatch_trip.trip_id)

            all_joined_trips = trip_ops.get_all_joined_trips(trip_log, 
                                                             next_to_dispatch_trip.trip_id)
            for that_trip in all_joined_trips:
                assert(that_trip.valid()), "Trip being written is invalid" # this needs to be true
                dict_writer.writerow(that_trip.__dict__)
                del trip_log[that_trip.trip_id]

            trip_buffer.popleft()
            trip_location_hash_table[pickup_pixel].popleft()

        else:
            break

    return

def receive_requests_now(reader, time, rollover_request):
    '''Listen for requests at this time from the stream'''
    if rollover_request is None:
        requests_now = list()
    else:
        requests_now = [rollover_request]
    while True:
        try:
            next_line = reader.next()
            trip = trip_ops.process_cleaned_trip(next_line)
            if trip.pickup_request_time > time:
                return requests_now, trip
            else:
                requests_now.append(trip)
        except StopIteration:
            return None, None

def handle_all_trip_requests(constraints):
    '''Main function'''
    fleet_size = constraints['fleet_size']
    beliefs = constraints['beliefs']
    local_demand_degree = constraints['local_demand_degree']
    freq_levrs = int(constraints['freq_levrs'])

    cleaned_filepath = generic_ops.cleaned_fp(constraints['raw'])
    result_filepath = generic_ops.results_fp(constraints['raw'], constraints['index'])

    #-------------------------------------------------------- START READER OPS
    inputfile = open(cleaned_filepath, 'rb')
    reader = csv.DictReader(inputfile)
    initial_trip_log = trip_ops.read_n_cleaned_trips(reader, fleet_size)
    #-------------------------------------------------------- END READER OPS


    #-------------------------------------------------------- START WRITER OPS
    open(result_filepath, 'w').close() # reset the output file
    outputfile = open(result_filepath, 'wa')
    keys = initial_trip_log.values()[0].__dict__.keys()
    dict_writer = csv.DictWriter(outputfile, keys)
    dict_writer.writeheader()
    for trip in initial_trip_log.values():
        dict_writer.writerow(trip.__dict__)
    #-------------------------------------------------------- END WRITER OPS

    # trip_location_hash_table is a data structure that is a dict of trip origin points,
    # each origin point contains a list of trips scheduled to leave from that point,
    # represented solely by the trip that is the first-stop of that trip

    # trip_buffer is a double-queue data structure that enqueues requests as they come in
    #   and dequeues them when they are dispatched.

    # trip_log is a dict that is synced with the trip_buffer,
    # contains more detailed info about trips

    trip_location_hash_table = dict()
    trip_buffer = deque()

    # Transform Trip Log to Be Index By Vehicle ID
    vehicles_log = initial_vehicle_log(initial_trip_log, fleet_size)
    # Get time of last initial pickup request
    start_time = initial_trip_log.values()[-1].pickup_request_time

    # Clear this variable to save memory
    initial_trip_log = None

    trip_log = dict()
    time = start_time
    rollover_request = None
    while True:
        requests, rollover_request = receive_requests_now(reader, time, rollover_request)

        # There are no incoming trip requests or trips left to dispatch. End Loop
        if requests is None and len(trip_buffer) == 0:
            break

        # There are trip requests this turn. Process them.
        if requests is not None and len(requests) >= 0:
            trip_log, vehicles_log, beliefs = \
                handle_requests_at_this_time(trip_log,
                                             vehicles_log,
                                             requests,
                                             constraints,
                                             trip_location_hash_table,
                                             trip_buffer,
                                             beliefs)
        counter = 0
        for pickup_pixel in trip_location_hash_table:
            counter += len(trip_location_hash_table[pickup_pixel])

        # Clear trips ready for dispatch at this time
        clear_trips_for_dispatch(trip_log,
                                 vehicles_log,
                                 constraints,
                                 trip_location_hash_table,
                                 trip_buffer,
                                 dict_writer)

        # LEVRS Handling
        if freq_levrs != 0 and time % freq_levrs == 0:
            vehicles_log = \
                handle_empty_repositioning(vehicles_log, time, beliefs, local_demand_degree)

        time += 1 # next iteration of time

    outputfile.close()

    assert(len(trip_log) == 0), "There were %s undispatched trips." % (str(len(trip_log)))

    return vehicles_log
