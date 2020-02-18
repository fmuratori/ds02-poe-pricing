import json

import requests
from collections import namedtuple

BASE_POE_API_URL = 'https://www.pathofexile.com/api/public-stash-tabs?id='

BLIGHT_NCI = '477096900-493708600-466167000-533102700-506542200'

BLIGHT_RANDOM_NCI = '480000000-499000000-470000000-550000000-510000000'

def json2obj(data):
    '''
    Convert a dict type object to a corresponding python custom object.
    '''
    return json.loads(data, object_hook=lambda y: namedtuple('X', y.keys())(*y.values()))


#_______________________ DOWNLOAD STASHES _______________________
def download_batch(next_change_id):
    '''
    Download single batch from poe stash tab API. A single batch contains multiple
    stashes.
    '''
    r = requests.get(url=BASE_POE_API_URL+next_change_id)
    return json2obj(r.text)

def download_multiple_batches(next_change_id, n_batches=2):
    '''
    Download a fixed number of batches. This function is similar to download_batch.
    '''

    res = list()
    for i in range(n_batches):
        data = download_batch(next_change_id)
        next_change_id = data.next_change_id

        res.append(data)
    return res

def batch_generator(next_change_id, n_batches=None, max_next_change_id=None):
    '''
    Download poe stash tab API batches throght a generator. The generation can
    be terminated both when at least n_batches of data have been provided or
    when the generation surpass a threshold.
    '''
    res = list()

    while (n_batches is not None and i in range(n_batches)) or \
        (max_next_change_id is not None and \
            sum([int('-'.split(max_next_change_id)[i]) < \
            int('-'.split(next_change_id)[i]) for i in range(5)]) < 3):

        data = download_batch(next_change_id)
        next_change_id = data.next_change_id

        yield data
