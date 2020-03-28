
from threading import Thread
import logging
import time

log = logging.getLogger(__name__)

class SimpleTransformer(Thread):
    '''
    Basic stashes handler procedure. This class simply save stashes data
    as json files with little to none processing to the source data.
    '''
    def __init__(self, u_lock, p_lock, u_list, p_list, config):
        Thread.__init__(self)

        self.u_lock = u_lock
        self.p_lock = p_lock
        self.u_list = u_list
        self.p_list = p_list
        self.config = config['TRANSFORM']
        self.sleep_time = int(self.config['SLEEP_TIME'])

        log.info('[T] - Initializing SimpleTransformer thread ...')

    def run(self):
        while True:
            # pick an element fron the unprocessed data list
            elem = None
            self.u_lock.acquire()
            u_list_size = len(self.u_list)
            if u_list_size > 0:
                elem = self.u_list.pop(0)
                u_list_size -= 1
            self.u_lock.release()

            if elem is not None:
                a = time.time()
                curr_nci, content, dtime = elem
                for i, stash in enumerate(content['stashes']):
                    if stash['league'] != 'Delirium' or not stash['public']:
                        del(content['stashes'][i])
                content['datetime'] = dtime.strftime("%m/%d/%Y, %H:%M:%S")
                b = time.time()

                # save stashes data into a syncronized list for processed data ready to be serialized
                self.p_lock.acquire()
                self.p_list.append((curr_nci, content))
                p_list_size = len(self.p_list)
                self.p_lock.release()

                log.info('[T] - Stashes processed in {} seconds.\tU_LIST_SIZE: {}\tP_LIST_SIZE: {}'.format(round(b-a, 2), u_list_size, p_list_size))
            else:
                log.info('[T] - no unprocessed data found. Sleep {} seconds...'.format(self.config['SLEEP_TIME']))
                time.sleep(self.sleep_time)

class DBTransformer(Thread):
    '''
    This handler process and save source data into postgres database tables.
    '''
    def __init__(self):
        raise NotImplementedError()
