from scipy.sparse import csr_matrix
import numpy as np
import pandas as pd
from scipy.sparse import lil_matrix, csr_matrix, vstack
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.preprocessing import MinMaxScaler, MaxAbsScaler
from abc import ABC, abstractmethod
from sklearn.base import BaseEstimator


INFLUENCES_COLUMNS = ['influence_crusader', 'influence_elder', 'influence_hunter',
                      'influence_redeemer', 'influence_shaper', 'influence_warlord']

REQUIREMENTS_COLUMNS = ['requirement_str', 'requirement_int',
                        'requirement_dex', 'requirement_level']

# ============================= SimpleEstimator features ==============================


class SimpleEstimator(BaseEstimator):
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return self._extract(X)

    def fit_transform(self, X, y=None):
        self.fit(X, y)
        return self.transform(X, y)

    @abstractmethod
    def _extract(self, X, y=None):
        pass


class IsAbyssJewel(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item'].sub_category.fillna('')
        feat = feat.apply(lambda y: 0 if y != 'abyss' else 1)
        return feat.values.reshape(-1, 1)


class IsSynthesised(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item'].synthesised.fillna(False)
        return (feat == True).astype(int).values.reshape(-1, 1)


class IsCorrupted(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item']['corrupted'].fillna(False)
        return (feat == True).astype(int).values.reshape(-1, 1)


class IsDuplicated(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item']['duplicated'].fillna(False)
        return (feat == True).astype(int).values.reshape(-1, 1)


class IsIdentified(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item'].identified.fillna(False)
        return (feat == True).astype(int).values.reshape(-1, 1)


class IsVeiled(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item'].num_veiled_modifiers.fillna(0)
        return feat.values.reshape(-1, 1)


class NumPrefixes(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item'].num_prefixes.fillna(0)
        return feat.values.reshape(-1, 1)


class NumSuffixes(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item'].num_suffixes.fillna(0)
        return feat.values.reshape(-1, 1)


class NumVeiledMods(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item'].num_veiled_modifiers.fillna(0)
        return feat.values.reshape(-1, 1)


class Category(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item'].category.fillna(0)
        return feat.values.reshape(-1, 1)


class SubCategories(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item'].sub_category.fillna(0)
        return feat.values.reshape(-1, 1)


class Ilvl(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item'].ilvl.fillna(0)
        return feat.values.reshape(-1, 1)


class SocketsCount(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item_socket'].groupby('item_id').count()

        # fill dataframe with empty rows
        missing_items_ids = set(
            X['trade_item'].id.values) - set(feat.index.values)
        feat = feat.append(pd.DataFrame(
            [{} for i in range(len(missing_items_ids))], index=missing_items_ids))
        feat.fillna(0, inplace=True)

        # order result
        feat = feat.loc[X['trade_item'].id.values, 'id']

        return feat.values.reshape(-1, 1)


class SocketsMaxGroupCount(SimpleEstimator):
    def _extract(self, X, y=None):
        # get socket groups cardinality
        feat = X['trade_item_socket'].groupby(
            ['item_id', 'socket_group']).count()
        # get biggest group for each item
        feat = feat.groupby(['item_id']).max()

        # fill dataframe with empty rows
        missing_items_ids = set(
            X['trade_item'].id.values) - set(feat.index.values)
        feat = feat.append(pd.DataFrame(
            [{} for i in range(len(missing_items_ids))], index=missing_items_ids))
        feat.fillna(0, inplace=True)

        # order result
        feat = feat.loc[X['trade_item'].id.values, 'id']
        return feat.values.reshape(-1, 1)


class Requirements(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item'][REQUIREMENTS_COLUMNS].fillna(0)
        return feat.values


class Influences(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item'][INFLUENCES_COLUMNS].fillna(False)
        return csr_matrix((feat == True).astype(int).values)


class Rarity(SimpleEstimator):
    def _extract(self, X, y=None):
        feat = X['trade_item'].rarity.fillna('')
        return feat.values.reshape(-1, 1)


# ============================= BaseEstimator features ==============================


class SocketColour(BaseEstimator):

    def fit(self, X, y=None):
        self._colours = set(X['trade_item_socket'].colour.values)
        return self

    def transform(self, X, y=None):
        feat = self._extract_colours(X)

        # fill dataframe with empty rows
        missing_items_ids = set(
            X['trade_item'].id.values) - set(feat.index.values)
        feat = feat.append(pd.DataFrame(
            [{} for i in range(len(missing_items_ids))], index=missing_items_ids))

        feat.fillna(0, inplace=True)

        feat = feat.loc[X['trade_item'].id.values].values
        return csr_matrix(feat)

    def _extract_colours(self, data):
        # count sockets by color for each item
        t = data['trade_item_socket'][['item_id', 'colour', 'id']
                                      ].groupby(['item_id', 'colour']).count()
        t.reset_index(inplace=True)

        # pivot table to have the colour of the sockets as columns
        t = pd.pivot(t, index='item_id', columns='colour')['id']
        t.fillna(0, inplace=True)

        # fill dataframe with empty columns
        for col in self._colours:
            if col not in t.columns:
                t[col] = 0

        # order columns following lookup table
        return t[self._colours]


# =============================== CLASS FEATURES ===============================


class Modifiers(BaseEstimator):
    def __init__(self, how='flag', chunk_size=100000):
        self.how = how
        self.chunk_size = chunk_size

    def fit(self, X, y=None):
        if self.how not in ['flag', 'mean', 'all']:
            raise ValueError()

        # create lookup table: modifier_id -> feature column index
        if self.how == 'all':
            self._modifiers = ['mod{}_value{}'.format(v['id'], i)
                               for _, v in X['modifier_type'].iterrows()
                               for i in range(v['text'].count('#') if '#' in v['text'] else 1)]
        else:
            self._modifiers = X['modifier_type'].id.apply(
                lambda y: 'mod{}'.format(y)).values
        return self

    def transform(self, X, y=None):
        # compute unnormalized features
        t = X['trade_item_modifier'].copy()
        t['value_agg'] = t[[colname for colname in t.columns if 'value' in colname]].mean(
            axis=1, skipna=True)
        if self.how == 'mean':
            t['value_agg'].fillna(1, inplace=True)
        elif self.how == 'flag':
            t['value_agg'] = 1
        elif self.how == 'all':
            # fill items modifiers with no value to 1
            t.loc[t.value_agg.isna(), 'value0'] = 1

        rows_iids = []
        features = []
        for chunk in self._split(t, self.chunk_size):
            if self.how in ['mean', 'flag']:
                chunk = pd.pivot_table(chunk, values='value_agg',
                                       index='item_id', columns='modifier_id')
            else:
                chunk = pd.pivot_table(chunk, values=['value0', 'value1', 'value2'],
                                       index='item_id', columns='modifier_id')
            chunk.columns = ['mod{}'.format(a) for a in chunk.columns]
            # fill Dataframe with empty colums representing unseen modifiers
            for colname in self._modifiers:
                if colname not in chunk.columns:
                    chunk[colname] = 0
            chunk.fillna(0, inplace=True)
            # order columns following lookup table
            features.append(csr_matrix(chunk[self._modifiers].values))
            rows_iids.extend(chunk.index.values)

        # create empty rows associated to items with no modifier
        missing_items_ids = set(X['trade_item'].id.values) - set(rows_iids)
        rows_iids.extend(missing_items_ids)

        features.append(csr_matrix(
            (len(missing_items_ids), len(self._modifiers))))
        features = vstack(features)

        return features[np.argsort(rows_iids), :]

    def _split(self, df, chunk_size):
        chunks = [df[i:i+chunk_size].copy()
                  for i in range(0, len(set(df.item_id.values)), chunk_size)]
        for i, chunk in enumerate(chunks):
            if i < len(chunks) - 1:
                while chunks[i].tail(1).item_id.values[0] == chunks[i+1].head(1).item_id.values[0]:
                    # move df row between chunks
                    chunks[i].append(chunks[1].head(1))
                    chunks[i+1].drop(index=chunks[i +
                                                  1].head(1).index.values, inplace=True)
        return chunks


class Properties(BaseEstimator):
    def __init__(self, how='flag'):
        self.how = how

    def fit(self, X, y=None):
        if self.how not in ['flag', 'mean', 'all']:
            raise ValueError()

        # create lookup table: property_id -> feature column index
        if self.how == 'all':
            # for each property, define how many columns are needed to represent data
            self._count_columns_per_property(X)

            self._properties = ['prop{}_value{}'.format(v['id'], i)
                                for _, v in X['property_type'].iterrows()
                                for i in range(v['count'])]

        else:
            self._properties = X['property_type'].id.apply(
                lambda y: 'prop{}'.format(y)).values

        return self

    def transform(self, X, y=None):
        t = self._extract_features(X)

        # create empty rows associated to items with no property
        missing_items_ids = set(
            X['trade_item'].id.values) - set(t.index.values)
        t = t.append(pd.DataFrame(
            [{} for i in range(len(missing_items_ids))], index=missing_items_ids))
        t.fillna(0, inplace=True)
        return csr_matrix(t.loc[X['trade_item'].id].values)

    def _extract_features(self, data):
        t = data['trade_item_property'].copy()

        if self.how == 'mean':
            t['value_agg'] = t[[colname for colname in t.columns if 'value' in colname]].mean(
                axis=1, skipna=True)
            t['value_agg'].fillna(1, inplace=True)
        elif self.how == 'flag':
            t['value_agg'] = 1

        if self.how == 'all':
            t = pd.pivot_table(
                t, values=['value0', 'value1'], index='item_id', columns='property_id')
            t.columns = ['prop{}_{}'.format(b, a) for a, b in t.columns]
        elif self.how in ['flag', 'mean']:
            t = pd.pivot_table(t, values='value_agg',
                               index='item_id', columns='property_id')
            t.columns = ['prop{}'.format(a) for a in t.columns]

        # fill dataframe with empty colums representing unseen properties
        for colname in self._properties:
            if colname not in t.columns:
                t[colname] = 0

        # order columns following lookup table
        t = t[self._properties]

        return t

    def _count_columns_per_property(self, items):
        values_per_property = []
        for k, v in items['property_type'].iterrows():
            count = 0
            for colname in ['value0', 'value1']:
                if all(~pd.isna(items['trade_item_property'][items['trade_item_property'].property_id == v['id']][[colname]].values)):
                    count += 1
            values_per_property.append(count)
        items['property_type']['count'] = values_per_property


# ============================== TARGET FEATURES ===============================


class Price(BaseException):
    def __init__(self, market_head=10, outlier_window=3, max_price_value=100000):
        '''
        - outlier_window: int
            Remove trades rate which value is outside the normal distribution window ?
            defined as (mean_value +- standard deviation * window).

        - market_head: int
            select only the top deals based on the exchange rate. Those deals most
            likely are the most representative of the currency exchange rates.
        '''
        self.market_head = market_head
        self.outlier_window = outlier_window
        self.max_price_value = max_price_value

    def fit(self, X, y=None):
        data, currencies = X
        self.currency_set = set(set(currencies.sell_currency.values) &
                                set(currencies.price_currency.values))

        self._extract_exchange_rates(currencies)

        return self

    def transform(self, X, y=None):
        data, currencies = X
        feat = np.zeros((len(data['trade_item']), 1))
        for i, (k, v) in enumerate(data['trade_item'].iterrows()):
            if v.price_currency != 'chaos':
                value = self.c_rates.loc['chaos',
                                         v.price_currency] * v.price_quantity
            else:
                value = v.price_quantity
            feat[i, 0] = value if value <= self.max_price_value else self.max_price_value
        return feat

    def _extract_exchange_rates(self, currencies):
        self.c_rates = pd.DataFrame(
            index=self.currency_set, columns=self.currency_set)
        currencies['rate'] = currencies.sell_quantity / \
            currencies.price_quantity

        for v1 in self.currency_set:
            v2 = 'chaos'
            if v1 == v2:
                value = 1
            else:  # we are interested only in converting over currencies to the "chaos" type
                temp = currencies[(currencies.sell_currency == v1) &
                                  (currencies.price_currency == v2)].copy()
                temp.sort_values('rate', ascending=False, inplace=True)
                temp['n_rate'] = temp.rate.apply(lambda y: (
                    y - temp.rate.mean()) / temp.rate.std())
                temp = temp[(temp.n_rate > -self.outlier_window) &
                            (temp.n_rate < self.outlier_window)].rate
                value = round(np.mean(temp.head(self.market_head)), 3)
            self.c_rates.loc[v1, v2] = value
