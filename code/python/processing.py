import os
import sys
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.join(os.path.realpath(__file__), os.pardir), os.pardir)))

import requests

import constants
import utilities as utils


def parseStashes():
    nextChangeId = constants.DEFAULT_NCI

    newData = []

    for i in range(100):
        print('Stash - {} - next_change_id: {}'.format(i, nextChangeId))

        nextChangeId, stashes = utils.getStashBatch(constants.DEFAULT_URL +
                                                    nextChangeId)
        for stash in stashes:
            if utils.isHealthyStash(stash) and 'Synthesis' in stash['league']:
                newStash = dict()
                newStash['stashName'] = stash['stash']
                newStash['stashType'] = stash['stashType']
                newStash['league'] = stash['league']
                newData.append(newStash)
        print(len(newData))


if __name__ == "__main__":
    parseStashes()