'''
This script represent the extract component of a ETL pipeline. Instead of
preventively save the next change ids from poe.ninja and consequently download
the stashes (which seems to be an ineffective procedure), here the goal is to
execute API calls to the stash tab api and immediately download the API
contents.

Some minor preprocessing will be applyed to limit the downloaded data size
'''
from threading import Thread
from datetime import datetime
import logging
import time
import json

from smart_open import open

log = logging.getLogger(__name__)

class APIProvider(Thread):
    def __init__(self, u_lock, u_list, config):
        Thread.__init__(self)
        log.info('[E] - Initializing APIProvider thread ...')

        self.u_lock = u_lock
        self.u_list = u_list
        self.config = config['EXTRACT']
        self.sleep_time = int(self.config['SLEEP_TIME'])

    def run(self):
        nci = self.config['STARTING_NCI']
        while True:

            a = time.time()
            url = self.config['API_URL'] + nci
            with open(url, 'rb') as file:
                content = json.load(file)
            b = time.time()

            if not self.isLast(content, nci):

                self.u_lock.acquire()
                self.u_list.append((nci, content, datetime.now()))
                u_list_size = len(self.u_list)
                self.u_lock.release()

                nci = content['next_change_id']

                log.info('[E] - Stashes downloaded in {} seconds.\t U_LIST_SIZE: {}'.format(round(b-a, 2), u_list_size))
            else:
                # if not enougt changes are detected, the thread sleeps 1 minute
                log.info('[E] - Reached head. Sleep {} seconds...'.format(self.config['SLEEP_TIME']))
                time.sleep(self.sleep_time)

    def isLast(self, content, curr_nci):
        return len(content['stashes']) == 0 or content['next_change_id'] == curr_nci

class FileSystemProvider(Thread):
    def __init__(self, u_lock, u_list, config):
        raise NotImplementedError()
