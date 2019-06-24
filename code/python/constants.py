import os

PROJECT_FOLDER = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)) + '/'

SEED = 42

CODE_FOLDER = PROJECT_FOLDER + 'code/'

DATA_FOLDER = PROJECT_FOLDER + 'data/'
RESOURCES_FOLDER = DATA_FOLDER + 'resources/'

LAST_NDI_SAVED_FILE = RESOURCES_FOLDER + 'last_nextChangeId.txt'

ORIGIN_DATA_FOLDER = DATA_FOLDER + 'market_origin/'

ORIGIN_TEST_DATA_FOLDER = DATA_FOLDER + 'market_origin_test/'

CURRENCIES_DATA_FOLDER = DATA_FOLDER + 'market_currencies/'
ITEMS_DATA_FOLDER = DATA_FOLDER + 'market_items/'


EXTERNAL_DATA_FOLDER = '/mnt/NILOX/origin/'

# poe API
DEFAULT_URL = 'https://www.pathofexile.com/api/public-stash-tabs?id='
DEFAULT_NCI = '348573430-360714130-340379780-391277850-368564540'
OPTIMAL_SYNTHESIS_NCI = '348573430-360714130-340379780-391277850-368564540'


# web scraping script
URL_POE_NINJA = 'https://poe.ninja/stats'
URL_STEAM_CHARTS = 'https://steamcharts.com/app/238960'
URL_GIT_HYP = 'https://www.githyp.com/path-of-exile-100607/?tab=player-count'
BROWSER_DRIVE = '/home/fabio/Desktop/ds02-poe-pricing/data/temp/geckodriver'
