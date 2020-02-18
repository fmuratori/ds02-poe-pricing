import logging
import time

from stash_api import stash

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

LEAGUE_NAME = 'Blight'
STARTING_NEXTCHANGEID = '477090000-493700000-466160000-533100000-506540000'

def build_nextchangeid(index, partial_nextchangeid):
    return '-'.join([str(partial_nextchangeid) if i == index else '0' for i in range(5)])

def search_league_nextchangeid(index, partial_nextchangeid, step_size):
    logging.info('Started recursive search: {} {}'.format(partial_nextchangeid, step_size))

    if step_size <= 10:
        return partial_nextchangeid

    while True:
        next_change_id, stashes = stash.get_stashes(build_nextchangeid(index, partial_nextchangeid))
        print(next_change_id)
        for stash_data in stashes:

            if stash.is_healthy_stash(stash_data) and LEAGUE_NAME in stash_data['league']:
                # found league in stash, recursively find a new best next_change_id
                return search_league_nextchangeid(index, int(partial_nextchangeid - step_size), int(step_size/10))

            if next_change_id.split('-')[index] == str(partial_nextchangeid):
                # league stashes have not been found
                raise ValueError('League {} has not been found. Try to lower the process execution step'.format(LEAGUE_NAME))
        partial_nextchangeid += step_size

def build_league_nextchangeid(initial_nextchangeid):
    results = []
    for i in range(5):
        logging.info('Searching for optimal partial next change id ...')

        start_time = time.time()

        best_partial_index = search_league_nextchangeid(i, int(initial_nextchangeid.split('-')[i]), 10000000)

        results.append(str(best_partial_index))

        end_time = time.time()

        logging.info('Task completed in {} seconds'.format(end_time - start_time))

    logging.info('Best nextChangeId for league {}: {}'. format(LEAGUE_NAME, '-'.join(results)))

if __name__ == "__main__":
    build_league_nextchangeid(STARTING_NEXTCHANGEID)

# 348573430-360714130-340379780-391277850-368564540
