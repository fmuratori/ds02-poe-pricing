from threading import Lock, Condition
from datetime import datetime
import configparser
import logging
import sys

from extract import Provider
from transform import Transformer
from load import Loader


# logging utility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
log = logging.getLogger(__name__)

# config variables
config = configparser.ConfigParser()
config.read('config.ini')

# thread concurrent structures
unpr_list_cond = Condition()
unpr_list = []

pr_list_cond = Condition()
pr_list = []

def class_from_string(cstring):
    return getattr(sys.modules[__name__], cstring)

if __name__== '__main__':
    extract_thread = Provider(unpr_list_cond, unpr_list, config)
    extract_thread.start()

    transform_thread = Transformer(unpr_list_cond, pr_list_cond,
                                   unpr_list, pr_list, config)
    transform_thread.start()

    load_thread = Loader(pr_list_cond, pr_list, config)
    load_thread.start()
