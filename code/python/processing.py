import requests

DEFAULT_URL = 'https://www.pathofexile.com/api/public-stash-tabs?id='
DEFAULT_NEXT_CHANGE_ID = '348573430-360714130-340379780-391277850-368564540'

def isHealthyStash(stash):
    return stash['stash'] is not None and stash['stashType'] is not None and stash['league'] is not None    

def parseStashes():
    nextChangeId = DEFAULT_NEXT_CHANGE_ID
    
    newData = []

    for i in range(100):
        print('Stash - {} - next_change_id: {}'.format(i, nextChangeId))

        url = DEFAULT_URL + nextChangeId        
        data = requests.get(url).json()
        nextChangeId = data['next_change_id']
        for stash in data['stashes']:
            if isHealthyStash(stash) and 'Synthesis' in stash['league']:
                newStash = dict()
                newStash['stashName'] = stash['stash']
                newStash['stashType'] = stash['stashType']
                newStash['league'] = stash['league']
                newData.append(newStash)
        print(len(newData))

if __name__ == "__main__":
    # findOptimalNextChangeId('Synthesis')
    parseStashes()


# 348573430-360714130-340379780-391277850-368564540