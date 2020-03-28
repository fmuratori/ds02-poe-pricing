from threading import Lock
from datetime import datetime
import configparser
import logging

from extract import FileSystemProvider, APIProvider
from transform import SimpleTransformer, DBTransformer
from load import SimpleLoader, DBLoader

# logging utility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

# config variables
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

unpr_list_lock = Lock()
unpr_list = []

pr_list_lock = Lock()
pr_list = []

if __name__== '__main__':
    # start thread

    extract_thread = APIProvider(unpr_list_lock, unpr_list, config)
    extract_thread.start()

    transform_thread = SimpleTransformer(unpr_list_lock, pr_list_lock, unpr_list, pr_list, config)
    transform_thread.start()

    load_thread = SimpleLoader(pr_list_lock, pr_list, config)
    load_thread.start()
