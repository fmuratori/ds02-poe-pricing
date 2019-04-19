import os
import sys
p = os.path.abspath('../')
sys.path.append(p)

import json
import requests

import constants
import utilities as utils


with open(constants.LAST_NDI_SAVED_FILE, 'r') as file:
        nextChangeId = file.read()

i = 1
while True:
    print('Loading stash n. {}: {}'.format(i, nextChangeId))
    i+=1

    nextChangeId, stashes = utils.getStashBatch(constants.DEFAULT_URL + nextChangeId)
    with open(constants.EXTERNAL_DATA_FOLDER + str(nextChangeId) + '.json', 'w') as file:
        file.write(json.dumps(stashes))

    with open(constants.LAST_NDI_SAVED_FILE, 'w+') as file:
        file.write(str(nextChangeId) + '\n')

