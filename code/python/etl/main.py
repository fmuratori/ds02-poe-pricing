import logging

import extract
import transform
import load

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
# logging.basicConfig(level=logging.INFO)
logging.getLogger(__name__)

if __name__ == '__init__':
    logging.info('Initializing process...')
    logging.info('Downloading batches starting from nextChangeId={} ...'.format(initial_nci))
    for batch in extract.batch_generator(next_change_id=)
        logging.info('Downloading batch...')
        start_time = time.time()

        # extract.

        end_time = time.time()
        logging.debug('Batch downloaded in {} seconds'.format(end_time - start_time))
