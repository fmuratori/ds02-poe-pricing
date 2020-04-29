
import os
import time
import json
from stat import S_ISREG, ST_CTIME, ST_MODE

import numpy as np

from smart_open import open

# retrieve paths variables
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
var = config['download_stashes']

def reached_new_nci(curr_nci, next_nci):
    next_nci = next_nci.split('-')
    curr_nci = curr_nci.split('-')
    return np.mean([int(v1) - int(v2) for v1, v2 in zip(curr_nci, next_nci)]) > 0

def get_checkpoint_nci():
    # get all entries in the directory
    ncis = [v.split('.')[0] for v in os.listdir(var['SAVE_PATH'])]
    if len(ncis) > 0:
        ncis_v0 = [v.split('-')[0] for v in ncis]

        return ncis[ncis_v0.index(max(ncis_v0))]
    return None

if __name__ == '__main__':

    # extract reference NCI data
    with open(var['NCI_FILE'], 'r') as file:
        lines = file.readlines()
    lines = [line.strip().split(' ') for line in lines]

    # search for the last downloaded file and get the next nci
    checkpoint_nci = get_checkpoint_nci()
    if checkpoint_nci:
        curr_nci = lines[0][2]
        while len(lines) > 0 and not reached_new_nci(curr_nci, checkpoint_nci):

            datetime = lines[0][0] + ' ' + lines[0][1]
            lines = lines[1:]
            curr_nci = lines[0][2]

        curr_nci = checkpoint_nci
        next_nci = lines[0][2]
    else:
        curr_nci = lines[0][2]
        next_nci = lines[1][2]
        datetime = lines[0][0] + ' ' + lines[0][1]

    print(curr_nci, next_nci)

    while len(lines) > 0:
        steps = 0
        start_time = time.time()
        while not reached_new_nci(curr_nci, next_nci):
            steps += 1
            # load json file from web
            with open(config['DEFAULT']['API_URL'] + curr_nci, 'rb') as source:
                # save json file to local folder
                with open(var['SAVE_PATH'] + curr_nci + '.json', 'w+') as dest:
                    stashes = json.load(source)
                    stashes['datetime'] = datetime
                    json.dump(stashes, dest)
            curr_nci = stashes['next_change_id']
        print('Reached new nextChangeId in {} steps and {} seconds'.format(
            steps, round(time.time() - start_time)))
        # remove the first item in the list and iter the process until
        # the list is empty
        lines = lines[1:]
        curr_nci = lines[0][2]
        next_nci = lines[1][2]
        datetime = lines[0][0] + ' ' + lines[0][1]
