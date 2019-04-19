import requests

def getStashBatch(url):
    data = requests.get(url).json()
    return data['next_change_id'], data['stashes']  

def isHealthyStash(stash):
    return stash['stash'] is not None and stash['stashType'] is not None and stash['league'] is not None    
