import os
import click
import types
import time
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack, vstack
import pickle
import logging
import configparser
from .learn import feature, preprocess
from .data import select

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
log = logging.getLogger(__name__)

CHUNK_SIZE = 10000


def split_dataframe(df, chunk_size=CHUNK_SIZE):
    chunks = list()
    for i in range(int(np.ceil(len(df) / chunk_size))):
        chunks.append(df[i*chunk_size:(i+1)*chunk_size])
    return chunks


def append_with_check(l, data, feat):
    start_time = time.time()

    if isinstance(feat, types.FunctionType):
        result = feat(data)
    else:
        result = feat.transform(data)
    end_time = time.time()
    log.debug('Feature {} extracted in {} seconds!'.format(
        feat, round(end_time - start_time, 2)))

    if isinstance(result, np.ndarray):
        result = csr_matrix(result)

    l.append(result)


@click.command()
@click.argument("connect")
@click.option("--save", default=None)
@click.option("--category", default='weapons')
def generate_features(connect, save, category):
    # data load
    if os.path.exists(connect):
        log.info('Loading connection file...')
        connect_config = configparser.ConfigParser()
        connect_config.read(connect)

        log.info('Loading data from database...')
        start_time = time.time()
        items = select._get_by_item_category(
            [category], connect_config['postgresql'], currency_types=['chaos', 'exalted'])

        currencies = select.get_currency(connect_config['postgresql'])
        log.info('Data loaded in {} seconds'.format(time.time() - start_time))
        log.info('Loaded features (name, shape):')
        print({v.shape for k, v in items.items()})

    # initialized serializable features
    log.info('Fitting serializable features ...')
    socketCol = feature.SocketColour()
    socketCol.fit(items)
    modifiers = feature.Modifiers(how='all')
    modifiers.fit(items)
    properties = feature.Properties(how='all')
    properties.fit(items)
    categories = feature.Category()
    categories.fit(items)
    # subCategories = feature.SubCategories()
    # subCategories.fit(items)
    rarity = feature.Rarity()
    rarity.fit(items)
    price = feature.Price(market_head=10, outlier_window=3)
    price.fit(items, currencies)

    end_time = time.time()
    log.info('Features fitted in {} seconds'.format(
        round(end_time - start_time, 2)))

    # feature extraction
    log.info('Generating features ...')
    start_time = time.time()
    X_tot = []
    chunks = split_dataframe(items['trade_item'])
    for i, chunk in enumerate(chunks):
        # split data into chunks to reduce memory usage
        chunk_start_time = time.time()

        chunk_items = items.copy()
        chunk_items['trade_item'] = chunk
        chunk_items['trade_item_modifier'] = chunk_items['trade_item_modifier'][
            chunk_items['trade_item_modifier'].item_id.isin(chunk.id)]
        chunk_items['modifier_type'] = chunk_items['modifier_type'][chunk_items['modifier_type'].id.isin(
            chunk_items['trade_item_modifier'].modifier_id)]
        chunk_items['trade_item_property'] = chunk_items['trade_item_property'][
            chunk_items['trade_item_property'].item_id.isin(chunk.id)]
        chunk_items['property_type'] = chunk_items['property_type'][chunk_items['property_type'].id.isin(
            chunk_items['trade_item_property'].property_id)]
        chunk_items['trade_item_socket'] = chunk_items['trade_item_socket'][
            chunk_items['trade_item_socket'].item_id.isin(chunk.id)]

        log.debug({k: v.shape for k, v in chunk_items.items()})

        X = list()
        append_with_check(X, chunk_items, feature.is_abyss_jewel)
        append_with_check(X, chunk_items, feature.synthesised)
        append_with_check(X, chunk_items, feature.corrupted)
        append_with_check(X, chunk_items, feature.duplicated)
        append_with_check(X, chunk_items, feature.identified)
        append_with_check(X, chunk_items, feature.num_prefixes)
        append_with_check(X, chunk_items, feature.num_suffixes)
        append_with_check(X, chunk_items, feature.num_veiled_mods)
        append_with_check(X, chunk_items, feature.requirements)
        append_with_check(X, chunk_items, feature.veiled)
        append_with_check(X, chunk_items, feature.influences)
        append_with_check(X, chunk_items, feature.sockets_count)
        append_with_check(X, chunk_items, feature.sockets_max_group_count)
        append_with_check(X, chunk_items, feature.ilvl)

        append_with_check(X, chunk_items, socketCol)
        append_with_check(X, chunk_items, modifiers)
        append_with_check(X, chunk_items, properties)
        append_with_check(X, chunk_items, categories)
        # append_with_check(X, chunk_items, subCategories)
        append_with_check(X, chunk_items, rarity)

        log.debug([v.shape for v in X])
        X = hstack(X)
        X_tot.append(X)

        chunk_end_time = time.time()
        log.info('Features extracted from chunk [{}/{}] in {} seconds.'.format(
            i + 1, len(chunks), round(chunk_end_time - chunk_start_time, 2)))

    # vertically merge together different sparse matrices with same number of columns
    X_tot = vstack(X_tot)
    end_time = time.time()
    log.info('Features generated in {} seconds. Shape {}'.format(
        round(end_time - start_time, 2), X_tot.shape))

    log.info('Generating dependant variable feature ...')
    y = price.transform(items, currencies)

    # save
    log.info('Saving generated features in {}'.format(save))
    if save is not None:
        with open(os.path.join(save, 'X_{}.pkl'.format(category)), 'wb+') as f:
            pickle.dump(X_tot, f)

        with open(os.path.join(save, 'y_{}.pkl'.format(category)), 'wb+') as f:
            pickle.dump(y, f)


if __name__ == '__main__':
    generate_features()
