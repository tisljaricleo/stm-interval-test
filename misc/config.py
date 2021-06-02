
def initialize_paths():
    """
    Paths for loading and saving data.
    :return: void
    """
    global DATA_PATH
    global LINKS_SPEED_LIMIT_PATH
    global ROUTES_PATH
    global ALL_TRANSITIONS_PKL_NAME
    global LIST_TRANSITIONS_PKL_NAME
    global SPATIAL_MATRIX_PKL_NAME

    # DATA_PATH = r'D:\DATA_\jadranski_most\okolica_jadranski.txt'    # Path to CSV raw data.
    # DATA_PATH = r'D:\DATA_\veliki_graf\rute.txt'
    DATA_PATH = r'D:\DATA_\Sordito_ZAGREB\data_zg.txt'
    LINKS_SPEED_LIMIT_PATH = r'speed_limits_processed.csv'
    ROUTES_PATH = r'outputs\routes'  # Name to save routes pickle.
    ALL_TRANSITIONS_PKL_NAME = r'outputs\transitions.pkl'   # Name for saving all transitions as pickle.
    LIST_TRANSITIONS_PKL_NAME = r'outputs\list_of_transitions.pkl'   # Name for saving list of transitions as pickle.
    SPATIAL_MATRIX_PKL_NAME = r'outputs\spatial_matrix.pkl'


def initialize_stm_setup():
    """
    Speed transition matrix setup.
    :return:
    """
    global RESOLUTION
    global MAX_INDEX
    global MAX_ITER
    global SPEED_LIST
    global SPEED_TYPE
    global SPEED_LIMIT_TRESH
    global SL_DOWN
    global SL_UP
    global DIAG_LOCS

    RESOLUTION = int(5)  # Resolution of the speed transition matrix in km/h
    MAX_INDEX = int(100 / RESOLUTION)  # Maximum index of the numpy array.
    MAX_ITER = int(100 + RESOLUTION)  # Maximal iteration for the range() function.
    SPEED_LIST = list(range(RESOLUTION, MAX_ITER, RESOLUTION))  # All speed values for rows/columns of the matrix.
    SPEED_TYPE = 'rel'
    SL_DOWN = 41
    SL_UP = 131
    SPEED_LIMIT_TRESH = 50

    diag_locs = []
    for i in range(0, MAX_INDEX):
        for j in range(0, MAX_INDEX):
            if i == j:
                diag_locs.append((i, j))
    DIAG_LOCS = diag_locs




def initialize_db_setup():
    global DB_NAME
    global ROUTE_COLLECTION
    global TRANSITION_COLLECTION
    global SM_COLLECTION
    global TENSOR_COLLECTION

    global SUMO_DB_NAME
    global SUMO_ROUTES_COLL
    global SUMO_GPS_COLL
    global SUMO_TRANS_COLL
    global SUMO_SM_COLLECTION
    global SUMO_SORTED_ROUTES_COLL

    DB_NAME = 'SpeedTransitionDB'
    ROUTE_COLLECTION = 'routesNEW'
    TRANSITION_COLLECTION = 'transitionsNEW'
    SM_COLLECTION = 'spatialMatrixRWLNEWrel'
    TENSOR_COLLECTION = 'spatialTensors'

    SUMO_GPS_COLL = 'SUMO_GPS'
    SUMO_ROUTES_COLL = 'SUMO_ROUTES'
    SUMO_SORTED_ROUTES_COLL = 'SUMO_ROUTES_SORTED'
    SUMO_TRANS_COLL = 'SUMO_TRANSITIONS'
    SUMO_DB_NAME = 'SUMO_DB'
    SUMO_SM_COLLECTION = 'SUMO_STMS'


def get_scenario():
    global SCENARIO_NORMAL_PATH
    global SCENARIO_NORMAL_NAME
    global SCENARIO_CONGESTED_PATH
    global SCENARIO_CONGESTED_NAME

    SCENARIO_NORMAL_PATH = r'.\data\scenario_normal.xml'
    SCENARIO_NORMAL_NAME = "S_NORMAL"
    SCENARIO_CONGESTED_PATH = r'.\data\scenario_congested.xml'
    SCENARIO_CONGESTED_NAME = "S_CONGESTED"

    # Choose one of the scenario types:
    scen_type = "NORMAL"
    # scen_type = "CONGESTED"

    if scen_type == "NORMAL":
        return SCENARIO_NORMAL_PATH, SCENARIO_NORMAL_NAME
    else:
        return SCENARIO_CONGESTED_PATH, SCENARIO_CONGESTED_NAME


def set_intervals():
    global INTERVAL_LENGTH      # Sets interval length in seconds.
    global INTERVAL_NUMBER      # Sets number of intervals.

    INTERVAL_LENGTH = 1800
    INTERVAL_NUMBER = 4
