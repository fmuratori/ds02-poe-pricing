import os
import sys
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.join(os.path.realpath(__file__), os.pardir), os.pardir)))

import json
import requests

import constants
import utilities as utils

nextChangeIdValues = None


def loadNextChangeIdFile():
    with open(constants.LAST_NDI_SAVED_FILE, 'r') as file:
        temp = file.readlines()

    global nextChangeIdValues
    if len(temp) == 0:
        nextChangeIdValues = ('0-0-0-0-0', None)
    elif len(temp) == 1:
        nextChangeIdValues = (temp[0].strip(), None)
    elif len(temp) == 2:
        nextChangeIdValues = (temp[0].strip(), temp[1].strip())
    else:
        raise ValueError()


def updateNextChangeId(initNextChangeId, finalNextChangeId):
    global nextChangeIdValues
    nextChangeIdValues = (initNextChangeId, finalNextChangeId)

    with open(constants.LAST_NDI_SAVED_FILE, 'w+') as file:
        file.write(str(initNextChangeId))
        if finalNextChangeId is not None:
            file.write('\n' + str(finalNextChangeId))


def getNextChangeIds():
    return (nextChangeIdValues[0], nextChangeIdValues[1])


def saveStashes():
    loadNextChangeIdFile()
    saveStash(nextChangeIdValues[0])


def saveStash(nextChangeId):
    # print('Loading stash: {}'.format(nextChangeIdValues[0]))
    if nextChangeIdValues[1] is not None and int(
            nextChangeId.split('-')[0]) > int(nextChangeIdValues[1].split('-')[0]):
        return


    newNextChangeId, stashes = utils.getIntegralStashBatch(constants.DEFAULT_URL +
                                                nextChangeIdValues[0])

    print('SAVE ', constants.ORIGIN_DATA_FOLDER + str(nextChangeId) + '.json')
    with open(constants.ORIGIN_DATA_FOLDER + str(nextChangeId) + '.json',
              'w+') as file:
        file.write(json.dumps(stashes))

    updateNextChangeId(newNextChangeId, nextChangeIdValues[1])
    saveStash(newNextChangeId)


if __name__ == "__main__":
    saveStashes()