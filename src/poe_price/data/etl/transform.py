from threading import Thread
import logging
import time
import re
from datetime import datetime
import pandas as pd

from . import transformer as tr

log = logging.getLogger(__name__)


class Transformer(Thread):
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
        self.t_policy = config['TRANSFORM']['TRANSFORM_POLICY']
        self.max_buffer_size = int(config['default']['BUFFER_SIZE'])

        # set the run method as one of the available policies
        exec('self.policy = self.{}'.format(self.t_policy))
        log.info(
            '[T] - Initialized transformer thread. Policy: {}'.format(self.t_policy))

    def run(self):
        while True:
            # if the buffer is full, wait for data to be removed to add new ones
            with self.p_cond:
                self.p_cond.wait_for(self._checkProcessedCond)

            # pick an element from the unprocessed data list or wait till new unprocessed data is provided
            elem = None
            with self.u_cond:
                self.u_cond.wait_for(self._checkUnprocessedCond)
                elem = self.u_list.pop(0)
                self.u_cond.notify_all()

            # execute data transformation corresponding to the policy selected (in the class constructor)
            a = time.time()
            elem = self.policy(*elem)
            b = time.time()

            # save data into a list dedicated for processed data ready to be serialized
            with self.p_cond:
                self.p_list.append(elem)
                self.p_cond.notify_all()

            log.info(
                '[T] - Stashes processed in {} seconds.'.format(round(b-a, 2)))

    def _checkUnprocessedCond(self):
        return len(self.u_list) > 0

    def _checkProcessedCond(self):
        return len(self.p_list) < self.max_buffer_size

    def simpleTransformer(self, curr_nci, content):
        content = tr.filter_json(content)
        return curr_nci, content

    def dbTransformer(self, curr_nci, content):
        items = tr.extract_items(content)

        currency = tr.extract_currencies(items)

        mitems, mitems_sockets, mitems_prop, mitems_prop_voc, mitems_mods, mitems_mods_voc = tr.extract_mod_items(
            items)

        return curr_nci, currency, mitems, mitems_sockets, mitems_prop, mitems_prop_voc, mitems_mods, \
            mitems_mods_voc
