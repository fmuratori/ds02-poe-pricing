import requests

DEFAULT_URL = 'https://www.pathofexile.com/api/public-stash-tabs?id='

def isHealthyStash(stash):
    return stash['stash'] is not None and stash['stashType'] is not None and stash['league'] is not None    

def findOptimalNextChangeId(leagueName):
    results = []
    for i in range(5):
        bestPartialIndex = searchLeague(leagueName, i, 0, 10000000)
        results.append(bestPartialIndex)
        print('Best: {} {}'.format(i, bestPartialIndex))
    print('Best nextChangeId for league {}: {}'. format(leagueName, results))

def searchLeague(leagueName, index, partialNextChangeId, stepSize):
    print('Started recursive search with params: {} {} {} {}'.format(leagueName, index, partialNextChangeId, stepSize))
    if stepSize < 10:
        return partialNextChangeId

    while True:
        data = requests.get(DEFAULT_URL + buildFullNextChangeId(index, partialNextChangeId)).json()
        nextChangeId = data['next_change_id']

        for stash in data['stashes']:
            if isHealthyStash(stash) and leagueName in stash['league']:
                return searchLeague(leagueName, index, int(partialNextChangeId - stepSize), int(stepSize/10))
            if nextChangeId.split('-')[index] == str(partialNextChangeId):
                return partialNextChangeId
        partialNextChangeId += stepSize

def buildFullNextChangeId(index, partialNextChangeId):
    return '-'.join([str(partialNextChangeId) if i == index else '0' for i in range(5)])

if __name__ == "__main__":
    findOptimalNextChangeId('Synthesis')

# 348573430-360714130-340379780-391277850-368564540