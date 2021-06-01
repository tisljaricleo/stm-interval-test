
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

db, client = database.init(config.SUMO_DB_NAME)

routes = dict({})
timestep = 0.0

limits = pd.read_csv(r'.\limits.csv', sep=';', index_col='id')
limits = limits.T.to_dict('list')


# putanja do fcd_jadranski
with open(r'fcdjadranski.xml') as file:
    for line in file:

        if "timestep time" in line:
            timestep = float(line.split('"')[1])
            continue

        if "vehicle id" in line:
            dict_data = json.loads('{' + line.strip().strip('<>/')[7:].replace('=', '":').replace(' ', ',"').replace(',', "", 1) + '}')

            dict_data["timestep"] = timestep
            dict_data["abs_speed"] = 3.6 * float(dict_data["speed"])

            try:
                speed_limit = limits[dict_data['lane'].split('_')[0]]
                # print('speed_limit: %s orig_lane: %s splited: %s' % (speed_limit, dict_data['lane'], dict_data['lane'].split('_')[0]))
                rel_speed = 3.6 * float(dict_data["speed"]) / speed_limit[0] * 100
                dict_data["rel_speed"] = round(rel_speed, 2)
            except Exception as e:
                print('Something went wrong!' + str(e))
                continue

            database.insertOne(db=db, collection=config.SUMO_GPS_COLL, data=dict_data)

            # if dict_data['id'] in routes.keys():
            #     routes[dict_data['id']].append(dict_data)
            # else:
            #     routes[dict_data['id']] = list([])
            #     routes[dict_data['id']].append(dict_data)

database.closeConnection(client=client)

t2 = get_time()
print('Exe time: {0}'.format(t2-t1))


'''
USE OF yield

def readInChunks(fileObj, chunkSize=2048):
    """
    Lazy function to read a file piece by piece.
    Default chunk size: 2kB.

    """
    while True:
        data = fileObj.read(chunkSize)
        if not data:
            break
        yield data

f = open('bigFile')
for chunk in readInChunks(f):
    do_something(chunk)
f.close()

'''