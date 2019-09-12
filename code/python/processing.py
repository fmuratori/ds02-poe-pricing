import os
import sys
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.join(os.path.realpath(__file__), os.pardir), os.pardir)))

import requests

import constants
import utilities as utils


def filterCurrencies(stashesBatch):

    for stash in stashesBatch:
        if utils.isHealthyStash(stash):
            for item in stash['items']:
                if 'currency' in item['category'].keys() and 'note' in item.keys():
                    print(item)



def parseStashesLocal():
    selectedFile = constants.ORIGIN_TEST_DATA_FOLDER + sorted(
        os.listdir(constants.ORIGIN_DATA_FOLDER))[0]

    while os.path.isfile(selectedFile):

        print('Loading local file ', selectedFile)

        nextChangeId, stashesBatch = utils.getStashBatch(selectedFile, isLocal=True)
        selectedFile = constants.ORIGIN_TEST_DATA_FOLDER + nextChangeId + '.json'

        filterCurrencies(stashesBatch)

        # filterItems()
# import json
# def temp():
#     allFiles = sorted(os.listdir(constants.ORIGIN_TEST_DATA_FOLDER))

#     realFileName = '348573430-360714130-340379780-391277850-368564540'
#     for i in range(len(allFiles)):
#         with open(constants.ORIGIN_TEST_DATA_FOLDER + allFiles[i], 'r') as file:
#             nextChangeId = allFiles[i].split('.')[0]
#             stashes = json.loads(file.readline())
#             data = json.dumps({'next_change_id':nextChangeId, 'stashes':stashes})

#         with open(constants.ORIGIN_TEST_DATA_FOLDER + 'temp/' + realFileName + '.json', 'w+') as outfile:
#             outfile.write(data)

#         realFileName = nextChangeId

def parseStashesWeb():
    selectedUrl = constants.DEFAULT_URL + '378897214-392539234-370229466-425411108-401252819'


    print('Loading web stash', selectedUrl)

    nextChangeId, stashes = utils.getStashBatch(selectedUrl)
    filterCurrencies()


if __name__ == "__main__":
    # parseStashesLocal()
    # parseStashesWeb()
    pass
