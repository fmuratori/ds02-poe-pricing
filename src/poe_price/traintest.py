import json
import time
import click
import logging

from inspect import isfunction, isclass
from scipy.sparse import issparse, csr_matrix, hstack
from smart_open import open

from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, accuracy_score, mean_absolute_error

from sklearn import *
from poe_price import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
log = logging.getLogger(__name__)

@click.command()
@click.option("--file", default=False, help="File system path to a json experiment configuration")
def from_json(file):
    log.info('Initialized json driven train-test procedure')
    log.info('Source file: {}'.format(file))

    # parse config file and traintest the model
    log.info('Loading configuration file ...')
    with open(file, 'r') as file:
        config = json.load(file)

    # get data
    log.info('Selecting data ...')
    (name, params), = config['select']['items'].items()
    items = eval(name)(**params)
    (name, params), = config['select']['currencies'].items()
    currencies = eval(name)(**params)
    #
    # # generate features
    # log.info('Extracting features ...')
    # X = []
    # for v in config['feature']['X']:
    #     start_time = time.time()
    #
    #     (name, params), = v.items()
    #     name = eval(name)
    #     if isfunction(name):
    #         feature = name(items, **params)
    #     elif isclass(name):
    #         name = name(**params)
    #         feature = name.fit_transform(items)
    #     X.append(feature if issparse(feature) else csr_matrix(feature))
    #
    #     end_time = time.time()
    #     log.info('Feature {} extracted in {} seconds'.format(name, round(end_time - start_time, 2)))
    # X = hstack(X)
    #
    # (name, params), = config['feature']['y'].items()
    # name = eval(name)
    # if isfunction(name):
    #     y = name(items, **params)
    # elif isclass(name):
    #     name = name(**params)
    #     y = name.fit_transform(items, currencies)
    #
    # # preprocess (remove null features, standardize / , split)
    # log.info('Preprocessing generated features ...')
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2,
    #                                                     random_state = 0)
    #
    # # train model
    log.info('Model training ...')
    start_time = time.time()

    (name, params), = config['model'].items()
    print(name, params)
    name = eval(name)
    regressor = name(**params)
    regressor.fit(X_train, y_train)

    end_time = time.time()
    log.info('Model {} trained in {} seconds'.format(name, round(end_time - start_time, 2)))

    y_train_pred = regressor.predict(X_train)
    y_test_pred = regressor.predict(X_test)

    log.info('Model testing ...')
    print(r2_score(y_train, y_train_pred), r2_score(y_test, y_test_pred))

    # test and metrics

    # serialize

if __name__ == '__main__':
    from_json()
