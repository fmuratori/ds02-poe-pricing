import os

PROJECT_FOLDER = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)) + '/'

SEED = 42

CODE_FOLDER = PROJECT_FOLDER + 'code/'

DATA_FOLDER = PROJECT_FOLDER + 'data/'
RESOURCES_FOLDER = DATA_FOLDER + 'resources/'
LAST_NDI_SAVED_FILE = RESOURCES_FOLDER + 'last_nextChangeId.txt'
ORIGIN_DATA_FOLDER = DATA_FOLDER + 'origin/'

EXTERNAL_DATA_FOLDER = '/mnt/NILOX/origin/'

# poe API
DEFAULT_URL = 'https://www.pathofexile.com/api/public-stash-tabs?id='
DEFAULT_NCI = '348573430-360714130-340379780-391277850-368564540'
OPTIMAL_SYNTHESIS_NCI = '348573430-360714130-340379780-391277850-368564540'
