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
import os

from smart_open import open

log = logging.getLogger(__name__)

class Provider(Thread):
    def __init__(self, u_cond, u_list, config):
        Thread.__init__(self)

        self.u_cond = u_cond
        self.u_list = u_list
        self.config = config['EXTRACT']

        # set the run method as one of the available policies
        exec("self.run = self.{}".format(self.config['EXTRACT_POLICY']))

        log.info('[E] - Initialized provider thread. Policy: {}'.format(self.config['EXTRACT_POLICY']))

    def apiProvider(self):
        nci = self.config['STARTING_NCI']
        while True:
            try:
                a = time.time()
                url = self.config['API_URL'] + nci
                with open(url, 'rb') as file:
                    content = json.load(file)
                b = time.time()
            except:
                # web resources are unreachable
                log.info('[E] Unreachable web resource: {}'.format(url))
                continue

            if len(content['stashes']) == 0 or content['next_change_id'] == nci:
                # if not enougt changes are detected, the thread sleeps 1 minute
                log.info('[E] - Reached last available stash. Sleep {} seconds...'.format(int(self.config['SLEEP_TIME'])))
                time.sleep(int(self.config['SLEEP_TIME']))
            else:
                with self.u_cond:
                    self.u_list.append((nci, content, datetime.now()))
                    self.u_cond.notify_all()    # wake up other threads waiting for new data to process
                    u_list_size = len(self.u_list)

                log.info('[E] - Data downloaded in {} seconds.\t U_LIST_SIZE: {}'.format(round(b-a, 2), u_list_size))

            nci = content['next_change_id']

            time.sleep(int(self.config['SLEEP_TIME']))

    def fsProvider(self):
        files_name = sorted(os.listdir(self.config['SOURCE_PATH']))
        while True:
            a = time.time()
            file_name = files_name.pop(0)
            with open(os.path.join(self.config['SOURCE_PATH'], file_name), 'rb') as file:
                content = json.load(file)
            b = time.time()

            with self.u_cond:
                self.u_list.append((file_name, content, datetime.strptime(content['datetime'], '%m/%d/%Y')))
                self.u_cond.notify_all()    # wake up other threads waiting for new data to process
                u_list_size = len(self.u_list)

            log.info('[E] - Data extracted in {} seconds.\t U_LIST_SIZE: {}'.format(round(b-a, 2), u_list_size))

            nci = content['next_change_id']

            if len(files_name) == 0:
                # if the last file has been reached, the thread must be stopped
                log.info('[E] - Reached last available stash. Terminating thread execution')
                break
