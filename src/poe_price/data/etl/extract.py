'''
This script represent the extract component of a ETL pipeline. Instead of
preventively save the next change ids from poe.ninja and consequently download
the stashes (which seems to be an ineffective procedure), here the goal is to
execute API calls to the stash tab api and immediately download the API
contents.

Some minor preprocessing will be applyed to limit the downloaded data size
'''
import re
import os
import time
import json
import logging
from threading import Thread
from datetime import datetime

from smart_open import open

log = logging.getLogger(__name__)


class Provider(Thread):
    def __init__(self, u_cond, u_list, config):
        Thread.__init__(self)

        self.u_cond = u_cond
        self.u_list = u_list

        # convert config data into object variables

        self.config = config['EXTRACT']
        self.e_policy = config['EXTRACT']['EXTRACT_POLICY']
        self.init_nci = config['EXTRACT']['STARTING_NCI']
        self.source_url = config['EXTRACT']['API_URL']
        self.sleep_time = int(config['EXTRACT']['SLEEP_TIME'])
        self.source_path = config['EXTRACT']['SOURCE_PATH']
        self.max_buffer_size = int(config['default']['BUFFER_SIZE'])

        t = config['EXTRACT']['STARTING_FILE']
        self.starting_file = t if re.match(
            '(\d*-){4}\d*.json', t) is not None else None

        # set the run method as one of the available policies
        exec("self.run = self.{}".format(self.e_policy))
        log.info(
            '[E] - Initialized provider thread. Policy: {}'.format(self.e_policy))

    def apiProvider(self):
        nci = self.init_nci
        while True:
            # if the buffer is full, wait for data to be removed to add new one
            with self.u_cond:
                self.u_cond.wait_for(self._checkUnprocessedCond)

            start_time = time.time()

            a = time.time()
            url = self.source_url + nci
            with open(url, 'rb') as file:
                content = json.load(file)
                content['datetime'] = str(datetime.now())
            b = time.time()

            if len(content['stashes']) == 0 or content['next_change_id'] == nci:
                # if no changes are detected, the thread sleeps 1 minute
                log.info(
                    '[E] - Reached last available stash. Sleep {} seconds...'.format(self.sleep_time))
                time.sleep(self.sleep_time)
            else:
                with self.u_cond:
                    self.u_list.append((nci, content))
                    self.u_cond.notify_all()

                log.info(
                    '[E] - Data downloaded in {} seconds.'.format(round(b-a, 2)))

            nci = content['next_change_id']

            exec_time = time.time() - start_time
            sleep_time = self.sleep_time - exec_time
            time.sleep(sleep_time if sleep_time > 0 else 0)

    def _checkUnprocessedCond(self):
        return len(self.u_list) < self.max_buffer_size

    def fsProvider(self):
        files_name = sorted(os.listdir(self.source_path))

        # jump to specific file
        if self.starting_file is not None:
            files_name = files_name[files_name.index(self.starting_file) + 1:]

        while True:
            with self.u_cond:
                if len(self.u_list) > self.max_buffer_size:
                    continue

            a = time.time()
            file_name = files_name.pop(0)
            with open(os.path.join(self.source_path, file_name), 'rb') as file:
                content = json.load(file)
            b = time.time()

            with self.u_cond:
                self.u_list.append((file_name, content))
                self.u_cond.notify_all()    # wake up other threads waiting for new data to process

            log.info('[E] - Data extracted in {} seconds.'.format(round(b-a, 2)))

            nci = content['next_change_id']

            if len(files_name) == 0:
                # if the last file has been reached, the thread must be stopped
                log.info(
                    '[E] - Reached last available stash. Terminating thread execution')
                break
