'''
This script represent the extract component of a ETL pipeline. Instead of
preventively save the next change ids from poe.ninja and consequently download
the stashes (which seems to be an ineffective procedure), here the goal is to
execute API calls to the stash tab api and immediately download the API
contents.

Some minor preprocessing will be applyed to limit the downloaded data size
'''
from threading import Thread, Lock
from datetime import datetime
import configparser
import logging as log
import time
import json

from smart_open import open
import numpy as np

# logging utility
log.basicConfig(level=log.INFO, format='%(asctime)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

# config variables
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
var = config['download_stashes_v2']

lock = Lock()
unpr_list = []

class StashProvider(Thread):
    def __init__(self):
        Thread.__init__(self)
        log.info('T1 - Initializing stash provider thread ...')

    def run(self):
        nci = config['download_stashes_v2']['STARTING_NCI']
        while True:

            a = time.time()
            # download stash
            url = config['DEFAULT']['API_URL'] + nci
            with open(url, 'rb') as file:
                content = json.load(file)
            b = time.time()

            if not self.isLast(content, nci):

                lock.acquire()
                unpr_list.append((nci, content, datetime.now()))
                ulsize = len(unpr_list)
                lock.release()

                nci = content['next_change_id']

                log.info('T1 - Stashes downloaded in {} seconds.\tQueue size: {}'.format(b-a, ulsize))
            else:
                # if not enougt changes are detected, the thread sleeps 1 minute
                log.info('T1 - Reached head, sleep...')
                time.sleep(60)

    def isLast(self, content, curr_nci):
        return len(content['stashes']) == 0 or content['next_change_id'] == curr_nci


class StashHandler(Thread):
    def __init__(self):
        Thread.__init__(self)
        log.info('T2 - Initializing stash handler thread ...')

    def run(self):
        while True:
            # pick an element fron the unprocessed data list
            elem = None
            lock.acquire()
            ulsize = len(unpr_list)
            if ulsize > 0:
                ulsize -= 1
                elem = unpr_list.pop(0)
            lock.release()

            if elem is not None:
                a = time.time()
                # filter list elementes
                curr_nci, content, dtime = elem

                for i, stash in enumerate(content['stashes']):
                    if stash['league'] != 'Delirium' or not stash['public']:
                        del(content['stashes'][i])
                # save
                content['datetime'] = dtime.strftime("%m/%d/%Y, %H:%M:%S")

                with open(var['SAVE_PATH'] + curr_nci + '.json', 'w+') as file:
                    json.dump(content, file)

                b = time.time()
                log.info('T2 - Stashes processed in {} seconds.\tQueue size: {}'.format(b-a, ulsize))


            else:

                log.info('T1 - no unprocessed data found. Sleep...')
                # sleep one minute
                time.sleep(60)


if __name__== '__main__':
    # start thread

    hthread = StashHandler()
    hthread.start()

    pthread = StashProvider()
    pthread.start()
