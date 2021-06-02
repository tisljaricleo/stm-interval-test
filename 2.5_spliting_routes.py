import pymongo
from misc import config

config.initialize_stm_setup()
config.initialize_db_setup()
config.set_intervals()
# Use string NORMAL or CONGESTED
scenario_path, scenario_name = config.get_scenario()

client = pymongo.MongoClient()
db = client[config.SUMO_DB_NAME]
SumoRoutesCol = db["{0}_{1}".format(config.SUMO_ROUTES_COLL, scenario_name)]
SumoRoutesSortedCol = db["{0}_{1}".format(config.SUMO_SORTED_ROUTES_COLL, scenario_name)]


def create_intervals(interval_length: int, n_intervals: int):
    """
    Creates the intervals for observations.
    :param interval_length: Length of the one interval in seconds.
    :param n_intervals: Number of intervals.
    :return: List of intervals.
    """
    return list(range(0, (interval_length * n_intervals) + 1, interval_length))


intervals = create_intervals(config.INTERVAL_LENGTH, config.INTERVAL_NUMBER)
all_routes = list(SumoRoutesCol.find({}, {"_id": 0}))
route_ids = []
database_entry = []
db_id = 0

for interval_id in range(len(intervals) - 1):
    begin_interval = intervals[interval_id]
    end_interval = intervals[interval_id + 1]

    database_entry.append({"data": [],
                           "interval": end_interval, "interval_range": str(begin_interval) + "-" + str(end_interval)})

    for route in all_routes:
        time = route['points'][0]['timestep']
        if begin_interval < time <= end_interval:
            route_ids.append(route['route_id'])
            continue

    if len(route_ids) == 0:
        database_entry[db_id]["data"] = None
    else:
        database_entry[db_id]["data"] = route_ids

    route_ids = []
    db_id += 1

try:
    SumoRoutesSortedCol.insert_many(database_entry)
except Exception as e:
    print("Database insert error!" + str(e))
