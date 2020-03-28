
from threading import Thread
import logging
import time

import json

log = logging.getLogger(__name__)

class SimpleLoader(Thread):
    '''
    Basic loader thread. Data is simply saved into a specific folder as a json file.
    '''
    def __init__(self, p_lock, p_list, config):
        Thread.__init__(self)

        self.p_lock = p_lock
        self.p_list = p_list
        self.config = config['LOAD']
        self.sleep_time = int(self.config['SLEEP_TIME'])

        log.info('[L] - Initializing SimpleLoader thread ...')

    def run(self):
        while True:
            # pick an element fron the unprocessed data list
            elem = None
            self.p_lock.acquire()
            p_list_size = len(self.p_list)
            if p_list_size > 0:
                elem = self.p_list.pop(0)
                p_list_size -= 1
            self.p_lock.release()

            if elem is not None:
                curr_nci, content = elem

                a = time.time()
                with open(self.config['SAVE_PATH'] + curr_nci + '.json', 'w+') as file:
                    json.dump(content, file)
                b = time.time()

                log.info('[L] - Stashes loaded in {} seconds.\tP_LIST_SIZE: {}'.format(round(b-a, 2), p_list_size))
            else:
                log.info('[L] - no processed data found. Sleep {} seconds...'.format(self.config['SLEEP_TIME']))
                time.sleep(self.sleep_time)

class DBLoader(Thread):
    '''
    This handler process and save source data into postgres database tables.
    '''
    def __init__(self):
        raise NotImplementedError()
