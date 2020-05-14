from threading import Condition
from datetime import datetime
import configparser
import logging
import sys
import os

import click

from .extract import Provider
from .transform import Transformer
from .load import Loader


# logging utility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
log = logging.getLogger(__name__)

@click.command()
@click.option("--file", default='config.ini', help="Configuration file containing etl procedure policy settings")
def initialize_etl(file):
    # config variables
    config = configparser.ConfigParser()
    __location__ = os.path.realpath(os.path.join(os.getcwd(),
    os.path.dirname(__file__))) # get absolute path of the directory containing this files
    config.read(os.path.join(__location__, 'config.ini'))

    # thread concurrent structures
    unpr_list_cond = Condition()
    unpr_list = []

    pr_list_cond = Condition()
    pr_list = []

    extract_thread = Provider(unpr_list_cond, unpr_list, config)
    extract_thread.start()

    transform_thread = Transformer(unpr_list_cond, pr_list_cond,
                                    unpr_list, pr_list, config)
    transform_thread.start()

    load_thread = Loader(pr_list_cond, pr_list, config)
    load_thread.start()

if __name__== '__main__':
    initialize_etl()