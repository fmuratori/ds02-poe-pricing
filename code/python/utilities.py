import os
import sys
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.join(os.path.realpath(__file__), os.pardir), os.pardir)))

import json

import requests
import constants

def downloadPage(url):
    return requests.get(url).json()

def loadFromFileSystem(filepath):
    with open(filepath, 'r') as file:
        return json.loads(file.readline())

def getStashBatch(url, returnIntegral=False, isLocal=False):
    if isLocal:
        data = loadFromFileSystem(url)
    else:
        data = downloadPage(url)

    if returnIntegral:
        return data['next_change_id'], data
    else:
        return data['next_change_id'], data['stashes']

def isHealthyStash(stash):
    return stash['stash'] is not None and stash[
        'stashType'] is not None and stash['league'] is not None
