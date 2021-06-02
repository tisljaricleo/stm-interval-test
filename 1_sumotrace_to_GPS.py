import json
import pandas as pd
import datetime
from misc.misc import get_time
from misc import database, config

print('Script {0} started ... '.format(__file__))
t1 = get_time()

config.initialize_paths()
config.initialize_stm_setup()
config.initialize_db_setup()
# Use string NORMAL or CONGESTED
scenario_path, scenario_name = config.get_scenario()

db, client = database.init(config.SUMO_DB_NAME)

routes = dict({})
timestep = 0.0
speed_limit = 130

with open(scenario_path) as file:
    for line in file:

        if "timestep time" in line:
            timestep = float(line.split('"')[1])
            continue

        if "vehicle id" in line:
            dict_data = json.loads(
                '{' + line.strip().strip('<>/')[7:].replace('=', '":').replace(' ', ',"').replace(',', "", 1) + '}')

            # Letter E represents input and output ramps and need to be excluded.
            if "E" in dict_data["lane"] or "gne" in dict_data["lane"]:
                continue

            dict_data["timestep"] = timestep
            dict_data["abs_speed"] = 3.6 * float(dict_data["speed"])

            rel_speed = float(dict_data["abs_speed"]) / speed_limit * 100
            dict_data["rel_speed"] = round(rel_speed, 2)

            try:
                database.insertOne(db=db,
                                   collection="{0}_{1}".format(config.SUMO_GPS_COLL, scenario_name),
                                   data=dict_data)
            except Exception as e:
                print('Database insert failed! Error:' + str(e))
            continue

database.closeConnection(client=client)

t2 = get_time()
print('Exe time: {0}'.format(t2 - t1))
