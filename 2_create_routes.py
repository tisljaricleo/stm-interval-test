import json
import pandas as pd
import datetime
from misc.misc import (get_time,
                       interval_sep,
                       get_date_parts)
from misc import database, config


def harmonic_speed(speed_data):
    hSum = 0
    for s in speed_data:
        if s == 0:
            hSum += 1
            continue
        hSum += 1 / s
    return len(speed_data) / hSum


print('Script {0} started ... '.format(__file__))
t1 = get_time()

config.initialize_paths()
config.initialize_stm_setup()
config.initialize_db_setup()
# Use string NORMAL or CONGESTED
scenario_path, scenario_name = config.get_scenario("NORMAL")

db, client = database.init(config.SUMO_DB_NAME)

midnight_time = 1598918400

route_ids = db["{0}_{1}".format(config.SUMO_GPS_COLL, scenario_name)].find().distinct('id')

no_trans_counter = 1

for route_id in route_ids:

    db_route = dict({})

    route = list(db["{0}_{1}".format(config.SUMO_GPS_COLL, scenario_name)].find({"id": route_id}).sort("timestep, 1"))

    points = list([])
    abs_speeds = list([])
    rel_speeds = list([])
    # i = 0

    ids = []
    for i in range(0, len(route) - 1):

        curr_id = route[i]['lane'].split('_')[0]
        next_id = route[i + 1]['lane'].split('_')[0]

        if curr_id == next_id:
            # If IDs are the same, save abs and rel speeds.
            # IDs must be different to have a transition and we want the harmonic speed
            # of the vehicle on one link.
            abs_speeds.append(float(route[i]['abs_speed']))
            rel_speeds.append(float(route[i]['rel_speed']))
            continue

        elif curr_id == next_id and i + 1 == len(route) - 1:
            # This means that you reached the end of the list. Then add the last known ID
            # with its corresponding speed values.
            time = midnight_time + int(route[i]['timestep'])

            if len(abs_speeds) > 0:
                a_s = harmonic_speed(abs_speeds)
                r_s = harmonic_speed(rel_speeds)
            else:
                a_s = route[i]['abs_speed']
                r_s = route[i]['rel_speed']

            point = dict({'link_id': curr_id,
                          'time': time,
                          'abs_speed': a_s,
                          'rel_speed': r_s,
                          'interval': interval_sep(time),
                          'timestep': int(route[i]['timestep'])})

            points.append(point)

            abs_speeds = list([])
            rel_speeds = list([])

        else:
            # If next id is not the same as current, that means that transition occurred, then
            # add the speed values to the list.
            time = midnight_time + int(route[i]['timestep'])

            if len(abs_speeds) > 0:
                a_s = harmonic_speed(abs_speeds)
                r_s = harmonic_speed(rel_speeds)
            else:
                a_s = route[i]['abs_speed']
                r_s = route[i]['rel_speed']

            point = dict({'link_id': curr_id,
                          'time': time,
                          'abs_speed': a_s,
                          'rel_speed': r_s,
                          'interval': interval_sep(time),
                          'timestep': int(route[i]['timestep'])})

            points.append(point)

            abs_speeds = list([])
            rel_speeds = list([])

    try:
        year, month, week, day, summer, working_day = get_date_parts(points[0]['time'])
    except IndexError:
        no_trans_counter += 1
        print("Warning! Route without transitions found. Count: {0}".format(no_trans_counter))
        continue

    db_route["points"] = points
    db_route["route_id"] = route_id
    db_route["summer"] = summer
    db_route["week"] = week
    db_route["working_day"] = working_day
    db_route["day"] = day
    db_route["month"] = month
    db_route["year"] = year

    database.insertOne(db=db,
                       collection="{0}_{1}".format(config.SUMO_ROUTES_COLL, scenario_name),
                       data=db_route)

database.closeConnection(client=client)

t2 = get_time()
print('Exe time: {0}'.format(t2 - t1))
