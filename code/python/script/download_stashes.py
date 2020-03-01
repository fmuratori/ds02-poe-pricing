from smart_open import open
import time
import json
import numpy as np

SAVE_PATH = '../../../data/temp/stashes_metamorth/'
API_URL = 'http://www.pathofexile.com/api/public-stash-tabs?id='

def reached_new_nci(curr_nci, next_nci):
    next_nci = next_nci.split('-')
    curr_nci = curr_nci.split('-')
    return np.mean([int(v1) - int(v2) for v1, v2 in zip(curr_nci, next_nci)]) > 0

# extract reference NCI data
NCI_FILE = '../../../data/next_change_id/scraping_results_test_2.txt'
with open(NCI_FILE, 'r') as file:
    lines = file.readlines()
lines = [line.strip().split(' ') for line in lines]

while len(lines) > 0:
    curr_nci = lines[0][2]
    next_nci = lines[1][2]

    steps = 0
    start_time = time.time()
    while not reached_new_nci(curr_nci, next_nci):
        steps += 1
        # load json file from web
        with open(API_URL + curr_nci, 'rb') as source:
            # save json file to local folder
            with open(SAVE_PATH + curr_nci + '.json', 'w+') as dest:
                stashes = json.load(source)
                json.dump(stashes, dest)
        curr_nci = stashes['next_change_id']
    print('Reached new nextChangeId in {} steps and {} seconds'.format(
        steps, round(time.time() - start_time)))
    # remove the first item in the list and iter the process until
    # the list is empty
    lines = lines[1:]
