"""Script generates spatial matrix as pandas DataFrame.
"""

import numpy as np
from misc.misc import rtm, get_time
from misc import database, config##
import pandas as pd

__author__ = "Leo Tisljaric"
__license__ = "GPL"
__version__ = "0.0.1"
__email__ = "ltisljaric@fpz.hr"
__status__ = "Development"


# def get_speed_limit(link_id):
#     #speed_limit = speed_data[speed_data.link_id == link_id].speed_limit.values
#     try:
#         speed_limit = speed_data[speed_data.link_id == str(link_id)].speed_limit.values[0]
#         #print()
#         # if speed_limit == 0:  # ako je speed limit nepoznat
#         #     speed_limit = 60
#     except:
#         speed_limit = 0  # ako nema zapisa u csv datoteci
#     return int(speed_limit)



def generate_spatial_matrix():
    speed_type = config.SPEED_TYPE

    int_query = database.selectDistinct(db=db, collection="SUMOTransitionsNew", attribute="interval", ret='list')
    intervals = sorted(int_query)

    # All unique transitions by origin and destination id
    unique_vals = list(database.groupBy(db=db,
                                        collection="SUMOTransitionsNew",
                                        query={'_id': {'origin_id': '$origin_id',
                                                       'destination_id': '$destination_id'}}))
    # List of tuples (origin_id, destination_id)
    ids = list([])
    for uv in unique_vals:  #tu ne povuće kak treba
        # sl_origin = get_speed_limit(uv['_id']['origin_id'])
        # sl_dest = get_speed_limit(uv['_id']['destination_id'])
        #
        # if (config.SL_DOWN <= sl_origin <= config.SL_UP) and (config.SL_DOWN <= sl_dest <= config.SL_UP):
        for k, v in uv.items():
            if 'origin_id' in v.keys():
                ids.append((uv['_id']['origin_id'], uv['_id']['destination_id']))

    br = 0
    for tr_id in range(0, len(ids)):

        br += 1
        if br % 1000 == 0:
            print(br)

        origin = ids[tr_id][0]
        destination = ids[tr_id][1]

        transition = (database.selectSome(db=db,
                                          collection=config.SUMO_TRANS_COLL,
                                          query={'origin_id': origin,
                                                 'destination_id': destination}))
        interval_dict = list([])
        
        all_origin_speeds = []
        all_dest_speeds = []

        for i in intervals:

            for t in transition:

                if t['interval'] != i:
                    continue

                orig_speed = rtm(t['origin_' + speed_type + '_speed'], config.RESOLUTION, speed_type)
                dest_speed = rtm(t['destination_' + speed_type + '_speed'], config.RESOLUTION, speed_type)
                
                all_origin_speeds.append(orig_speed)
                all_dest_speeds.append(dest_speed)

            transition_matrix = generate_trans_matrix(all_origin_speeds, all_dest_speeds)
            
            all_origin_speeds = []
            all_dest_speeds = []

            data = {'season': 'winter',
                    'stm': transition_matrix}

            interval_dict.append({'stm': data, 'interval_id': i})


        database.insertOne(db=db,
                           collection=(config.SUMO_SM_COLLECTION + str(speed_type)),
                           data={'origin_id': origin,
                                 'destination_id': destination,
                                 'intervals': interval_dict})


def generate_trans_matrix(origin_speeds, dest_speeds):

    resolution, max_index = config.RESOLUTION, config.MAX_INDEX

    t_matrix = np.zeros((max_index, max_index))

    if len(origin_speeds) > 0 and len(dest_speeds) > 0:
        for i in range(0, len(origin_speeds)):

            ############################################
            # (absolute) If the speed is larger than 100 and less than 140
            # (relative) If the relative speed is larger than 110%
            if origin_speeds[i] == None or dest_speeds[i] == None:
                continue
            ###############################################



            c_route_speed_index = int(origin_speeds[i] / resolution - 1)
            n_route_speed_index = int(dest_speeds[i] / resolution - 1)


            t_matrix[c_route_speed_index, n_route_speed_index] += 1
        return t_matrix.astype('int').tolist()
    else:
        return t_matrix.astype('int').tolist()


print('Script {0} started ... '.format(__file__))
t1 = get_time()
config.initialize_paths()
config.initialize_stm_setup()
config.initialize_db_setup()

# speed_data = pd.read_csv(r'limits.csv',
#                          names=['link_id', 'speed_limit'],
#                          sep=';',
#                          engine='c')

db, client = database.init(config.SUMO_DB_NAME)
generate_spatial_matrix()

database.closeConnection(client=client)

t2 = get_time()
print('Exe time: {0}'.format(t2 - t1))
