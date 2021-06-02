import pymongo
import numpy as np
import matplotlib.pyplot as plt
import misc.config as config
import math
from scipy.spatial import distance


def get_mass_center(m):
    max_val = 0.2 * np.max(m)  # Filter: remove 20% of maximal value.
    m = np.where(m < max_val, 0, m)
    m = m / np.sum(m)
    # marginal distributions
    dx = np.sum(m, 1)
    dy = np.sum(m, 0)
    # expected values
    X, Y = m.shape
    cx = np.sum(dx * np.arange(X))
    cy = np.sum(dy * np.arange(Y))
    return int(cx), int(cy)


def from_origin_distance(point):
    """Computes distance from center of mass to origin of the STM (0,0)

    :param point: Center of mass
    :type point: tuple
    :return: Euclidean distance from center of mass to origin of the STM
    :rtype: float
    """
    max_point = (config.MAX_INDEX, config.MAX_INDEX)
    origin = (0, 0)
    max_d = distance.euclidean(origin, max_point)
    return round(distance.euclidean(origin, point) / max_d, 2)


def plot_heatmap(data, title, output='show', filename='image.png'):
    """
    Plots heatmap for all speed transitions.
    :param data: 2D numpy array.
    :param states_names: State names (x and y labels).
    :param title: Title for ploting.
    :param output:
    :param filename:
    :return:
    """
    states_names = config.SPEED_LIST
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(data, cmap='cividis', interpolation='none')
    ax.set_xticks(np.arange(len(states_names)))
    ax.set_yticks(np.arange(len(states_names)))
    ax.set_xticklabels(states_names)
    ax.set_yticklabels(states_names)
    plt.xlabel('Destination speed (%)')
    plt.ylabel('Origin speed (%)')
    ax.set_title(title)
    fig.tight_layout()
    if output == 'show':
        plt.show()
    if output == 'save':
        plt.savefig(filename, bbox_inches='tight')


config.initialize_paths()
config.initialize_stm_setup()
config.initialize_db_setup()
# Use string NORMAL or CONGESTED
scenario_path, scenario_name = config.get_scenario()

client = pymongo.MongoClient()

db = client[config.SUMO_DB_NAME]
mycol = db["{0}_{1}".format(config.SUMO_SM_COLLECTION, scenario_name)]


n_congested = 0
n_unstable = 0
n_free_flow = 0


all_stm_data = list(mycol.find().sort("origin_id"))
for stm_data in all_stm_data:
    for interval in stm_data["intervals"]:
        stm = np.array(interval["stm"]["stm"])

        if np.sum(stm) == 0:
            continue

        try:
            xc_, yc_ = get_mass_center(stm)
            dist = from_origin_distance(point=(xc_, yc_))

            traffic_state = "free-flow"

            if dist < 0.33:
                traffic_state = "congested"
                n_congested += 1
            elif 0.33 < dist <= 0.66:
                traffic_state = "unstable"
                n_unstable += 1
            elif dist > 0.66:
                traffic_state = "free-flow"
                n_free_flow += 1
            else:
                traffic_state = "unknown"

            print(
                "xc:\t{0}\tyc:{1}\tinterval:{2}\tdistance:{3}\tstate:{4}\torigin_id:{5}\tdestination_id:{6}".format(xc_,
                                                                                                                    yc_,
                                                                                                                    interval['interval_id'],
                                                                                                                    dist,
                                                                                                                    traffic_state,
                                                                                                                    stm_data['origin_id'],
                                                                                                                    stm_data['destination_id']))

            # if dist < 0.33:
            #     plot_heatmap(stm, str(interval['interval_id']))

        except ValueError:
            print()

print("N_CONGESTED:{0}\tN_UNSTABLE:{1}\tN_FREEFLOW:{2}".format(n_congested, n_unstable, n_free_flow))
