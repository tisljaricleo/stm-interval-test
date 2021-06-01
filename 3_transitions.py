"""Script generates all transitions and transitions by same origin and destination id.
"""

from math import ceil
from misc import database, config
from misc.misc import get_time
import datetime
import pymongo
import numpy as np
import misc.config as config

__author__ = "Leo Tisljaric"
__license__ = "GPL"
__version__ = "0.0.1"
__email__ = "ltisljaric@fpz.hr"
__status__ = "Development"


def generate_transitions(routes):
    """Generate every transition from routes. Transition is defined as spatial change from link i to link i+1.

    Every row in dataframe that is returned consists of:
    'origin_id': ,
    'destination_id': ,
    'origin_speed': ,
    'destination_speed': ,
    'time': UTC time,
    'route_id': r['route_id'],
    'summer': r['summer'],
    'week': r['week'],
    'working_day': r['working_day'],
    'day': r['day'],
    'month': r['month'],
    'year': r['year'],
    interval': row['interval']

    :param routes: List of dictionaries. One dictionary represents the route data.
    :return: Pandas dataframe containing transitions.
    """
    transitions = list([])
    # t1 = datetime.datetime.now()

    for r in routes:
        for i in range(0, len(r['points']) - 1):
            row = r['points'][i]
            next_row = r['points'][i + 1]
            transitions.append({'origin_id': row['link_id'],
                                'destination_id': next_row['link_id'],
                                'origin_abs_speed': row['abs_speed'],
                                'destination_abs_speed': next_row['abs_speed'],
                                'origin_rel_speed': row['rel_speed'],
                                'destination_rel_speed': next_row['rel_speed'],
                                'time': row['time'],
                                'route_id': r['route_id'],
                                'summer': r['summer'],
                                'week': r['week'],
                                'working_day': r['working_day'],
                                'day': r['day'],
                                'month': r['month'],
                                'year': r['year'],
                                'interval': br + 1})
    try:
        #spremi unutar collectiona
        #intervali[br]["transitions"] = transitions
        database.insertMany(db, "SUMOTransitionsNew", transitions)


    except TypeError:
        print("prazna lista")

print('Script {0} started ... '.format(__file__))
t1 = get_time()
config.initialize_paths()
config.initialize_stm_setup()
config.initialize_db_setup()


client = pymongo.MongoClient()
db = client["SUMOSpeedTransitionDB"]
SUMOTransitions = db["SUMOTransitionsNew"]
# stvoren coll ovisno o broju intervala

db, client = database.init(config.SUMO_DB_NAME)

routes_ = list([])

# routes_ = database.selectSkipLimit(db, "SUMORoutesSorted", skip=skip_step, limit=limit)
route_ids = database.selectAll(db, "SUMORoutesSorted", ret="list")

RoutesFull = database.selectAll(db, "SUMORoutes", ret="list")


intervali= list([])
for br in range(1, 25):
    intervali.append(dict({}))


br = 0
for x in route_ids:
    for y in x["data"]:
        idruta = y

        for z in RoutesFull:
            if idruta == z["route_id"]:
                routes_.append(z)
    print("a")
    generate_transitions(routes_)
    br += 1
    routes_ = list([])

    #ovdje rute generiraj i ocisti Rputes_... slozi jos da spremi svaki coloection u zaseban interval
print("izasao")
#generate_transitions(routes_)
SUMOTransitions.insert_many(intervali)
#try:
#  SUMOTransitions.insert_many(intervali)
#except:
 #   print("GRESKA!")


database.closeConnection(client=client)

t2 = get_time()
print('Exe time: {0}'.format(t2 - t1))
