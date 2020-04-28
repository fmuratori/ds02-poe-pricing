
from threading import Thread
import logging
import time

import json

log = logging.getLogger(__name__)

class SimpleLoader(Thread):
    '''
    Basic loader thread. Data is simply saved into a specific folder as a json file.
    '''
    def __init__(self, p_cond, p_list, config):
        Thread.__init__(self)

        self.p_cond = p_cond
        self.p_list = p_list
        self.config = config['LOAD']
        self.sleep_time = int(self.config['SLEEP_TIME'])

        log.info('[L] - Initialized SimpleLoader thread')

    def run(self):
        while True:
            # pick an element fron the unprocessed data list
            with self.p_cond:
                self.p_cond.wait_for(self.check_processed_cond)

                elem = self.p_list.pop(0)

                p_list_size = len(self.p_list)


            curr_nci, content = elem

            a = time.time()
            with open(self.config['SAVE_PATH'] + curr_nci + '.json', 'w+') as file:
                json.dump(content, file)
            b = time.time()

            log.info('[L] - Stashes loaded in {} seconds.\tP_LIST_SIZE: {}'.format(round(b-a, 2), p_list_size))

    def check_processed_cond(self):
        with self.p_cond:
            return len(self.p_list)

class DBLoader(Thread):
    '''
    This handler process and save source data into postgres database tables.
    '''
    def __init__(self):
        raise NotImplementedError()
