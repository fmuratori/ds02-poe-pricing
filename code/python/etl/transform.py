
from threading import Thread
import logging
import time

log = logging.getLogger(__name__)

class SimpleTransformer(Thread):
    '''
    Basic stashes handler procedure. This class simply save stashes data
    as json files with little to none processing to the source data.
    '''
    def __init__(self, u_cond, p_cond, u_list, p_list, config):
        Thread.__init__(self)

        self.u_cond = u_cond
        self.p_cond = p_cond
        self.u_list = u_list
        self.p_list = p_list
        self.config = config['TRANSFORM']
        self.sleep_time = int(self.config['SLEEP_TIME'])

        log.info('[T] - Initialized SimpleTransformer thread')

    def run(self):
        while True:
            # pick an element fron the unprocessed data list
            elem = None
            with self.u_cond:
                # wait for new data to be processed
                self.u_cond.wait_for(self.check_unprocessed_cond)
                
                elem = self.u_list.pop(0)
                u_list_size = len(self.u_list)

            a = time.time()
            curr_nci, content, dtime = elem
            for i, stash in enumerate(content['stashes']):
                if stash['league'] != 'Delirium' or not stash['public']:
                    del(content['stashes'][i])
            content['datetime'] = dtime.strftime("%m/%d/%Y, %H:%M:%S")
            b = time.time()

            with self.p_cond:
                # save stashes data into a syncronized list for processed data ready to be serialized
                self.p_list.append((curr_nci, content))
                # wake up other threads waiting for new data to process
                self.p_cond.notify_all()

                p_list_size = len(self.p_list)

            log.info('[T] - Stashes processed in {} seconds.\tU_LIST_SIZE: {}\tP_LIST_SIZE: {}'.format(round(b-a, 2), u_list_size, p_list_size))

    def check_unprocessed_cond(self):
        with self.u_cond:
            return len(self.u_list) > 0

class DBTransformer(Thread):
    '''
    This handler process and save source data into postgres database tables.
    '''
    def __init__(self):
        raise NotImplementedError()
