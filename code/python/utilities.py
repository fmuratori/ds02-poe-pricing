import os
import sys
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.join(os.path.realpath(__file__), os.pardir), os.pardir)))

import requests


def downloadPage(url):
    return requests.get(url).json()


def getStashBatch(url):
    data = downloadPage(url)
    return data['next_change_id'], data['stashes']


def getIntegralStashBatch(url):
    data = downloadPage(url)
    return data['next_change_id'], data


def isHealthyStash(stash):
    return stash['stash'] is not None and stash[
        'stashType'] is not None and stash['league'] is not None
