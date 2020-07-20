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
@click.argument("connect", default='connect.ini')
@click.argument("etl", default='config.ini')
def etl_from_config(connect, etl):
    # config variables
    connect_config = configparser.ConfigParser()
    connect_config.read(connect)
    etl_config = configparser.ConfigParser()
    etl_config.read(etl)

    # thread concurrent structures
    unpr_list_cond = Condition()
    unpr_list = []

    pr_list_cond = Condition()
    pr_list = []

    extract_thread = Provider(unpr_list_cond, unpr_list, etl_config)
    extract_thread.start()

    transform_thread = Transformer(unpr_list_cond, pr_list_cond,
                                    unpr_list, pr_list, etl_config)
    transform_thread.start()

    load_thread = Loader(pr_list_cond, pr_list, etl_config, connect_config)
    load_thread.start()

if __name__== '__main__':
    etl_from_config()