import pymongo
import numpy as np
import matplotlib.pyplot as plt
import misc.config as config


def get_mass_center(m):
    max_val = 0.2 * np.max(m)   # Filter: remove 20% of maximal value.
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

config.initialize_stm_setup()
client = pymongo.MongoClient()
db= client["SUMOSpeedTransitionDB"]
mycol= db["SUMOspatialMatrixrel"]

data = list(mycol.find())
for x in data:
    for interval in x["intervals"]:
        stm = interval["stm"]["stm"]
        mm = np.array(stm)

        if np.sum(mm) == 0:
            continue

        try:
            xc_, yc_ = get_mass_center(mm)
            print("xc:\t{0}\tyc:{1}\tinterval:{2}".format(xc_, yc_, interval['interval_id']))
            if xc_ < 10:
                plot_heatmap(mm, str(interval['interval_id']))

        except ValueError:
            print()





