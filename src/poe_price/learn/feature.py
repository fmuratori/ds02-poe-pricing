import numpy as np
import pandas as pd
from scipy.sparse import lil_matrix, csr_matrix
from sklearn.preprocessing import LabelEncoder, OneHotEncoder


# ============================== COMMON FUNCTIONS ==============================


# ============================= FUNCTION FEATURES ==============================
def corrupted(data):
    return data['trade_item'].corrupted.fillna(False).astype(int).values.reshape(-1, 1)


def duplicated(data):
    return data['trade_item']['duplicated'].fillna(False).astype(int).values.reshape(-1, 1)


def identified(data):
    return data['trade_item'].identified.fillna(False).astype(int).values.reshape(-1, 1)


def suffixes_subcount(data):
    columns = [column for column in data['trade_item'].columns
               if column in ['num_veiled_mods', 'num_prefixes', 'num_suffixes']]
    return data['trade_item'].loc[:, columns].fillna(0).values


def requirements(data):
    columns = [column for column in data['trade_item'].columns
               if 'requirement' in column]
    return data['trade_item'].loc[:, columns].fillna(0).values


def veiled(data, how='flag'):
    '''
    how: 'flag', 'count' or 'both' to extract respectively a binary value,
         count of veiled mods or both of the previous values.
    '''
    data['trade_item'].num_veiled_modifiers.fillna(0, inplace=True)
    if how == 'flag':
        feature = data['trade_item'].num_veiled_modifiers.apply(lambda y: 1
                                                                if y > 0 else 0).values.reshape(-1, 1)
    elif how == 'count':
        feature = data['trade_item'].num_veiled_modifiers.values.reshape(-1, 1)
    elif how == 'both':
        feature = np.column_stack((veiled(data, how='flag'),
                                   veiled(data, how='count')))
    else:
        raise ValueError()
    return feature


def influences(data):
    columns = [
        column for column in data['trade_item'].columns if 'influence' in column]

    feature = data['trade_item'].loc[:, columns].fillna(False)
    feature.loc[:, :] = feature.loc[:, :].astype(int)

    return csr_matrix(feature.values)


def sockets(data):
    features = np.zeros((data['trade_item'].shape[0], 7))
    for k, iid in enumerate(data['trade_item'].id.values):
        sockets = data['trade_item_socket'][data['trade_item_socket'].item_id == iid]
        scolors = sockets.colour.value_counts()
        features[k, 0] = sockets.shape[0]
        features[k, 1] = scolors['R'] if 'R' in scolors else 0
        features[k, 2] = scolors['G'] if 'G' in scolors else 0
        features[k, 3] = scolors['B'] if 'B' in scolors else 0
        features[k, 4] = scolors['W'] if 'W' in scolors else 0
        features[k, 5] = scolors['A'] if 'A' in scolors else 0

        features[k, 6] = sockets.socket_group.value_counts().iloc[0] \
            if len(sockets) > 0 else 0
    return csr_matrix(features)


def is_abyss_jewel(data):
    return data['trade_item'].sub_category.apply(lambda y: 0 if y is None or y != 'abyss' else 1).values.reshape(-1, 1)

# =============================== CLASS FEATURES ===============================


class Modifiers:
    def __init__(self, how='flag'):
        '''
        how: method used to estract items modifiers value. if 'flag', items
             modifiers will be represented in a one-hot encoded fashion. If 'mean',
             items modifiers multiple values will be averaged to extract a single
             significant number.

        Flag type modifiers will be always represented with a simbolic value set
        to 1.
        '''
        if how not in ['flag', 'mean']:
            raise ValueError()
        self.how = how

    def fit_transform(self, data):
        # extract modifiers lookup table
        self.modifiers_lut = {pid: i for i, pid in enumerate(
            sorted(set(data['trade_item_modifier'].modifier_id.values)))}

        return self.transform(data)

    def transform(self, data):
        modifiers_feature_matrix = lil_matrix((data['trade_item'].shape[0],
                                               len(self.modifiers_lut)))

        for i, wid in enumerate(data['trade_item'].id.values):
            for pid, mod in data['trade_item_modifier'][data['trade_item_modifier'].item_id == wid].iterrows():
                if mod.modifier_id in self.modifiers_lut:
                    # select not null values of a modifier
                    values = [v for v in [mod.value0, mod.value1,
                                          mod.value2] if v is not None and not np.isnan(v)]
                    if len(values) > 0 and self.how == 'mean':
                        values = np.mean(values)
                    elif len(values) == 0 or self.how == 'flag':
                        values = 1

                    modifiers_feature_matrix[i,
                                             self.modifiers_lut[mod.modifier_id]] = values

        return modifiers_feature_matrix


class Properties:
    def __init__(self, how='flag'):
        '''
        how: method used to estract items properties value. if 'flag', items
             properties will be represented in a one-hot encoded fashion. If 'mean',
             items properties multiple values will be averaged to extract a single
             significant number.

        Flag type properties will be always represented with a simbolic value set
        to 1.
        '''
        if how not in ['flag', 'mean']:
            raise ValueError()
        self.how = how

    def fit_transform(self, data):
        # extract properties lookup table
        self.properties_lut = {pid: i for i, pid in enumerate(
            sorted(set(data['trade_item_property'].property_id.values)))}

        return self.transform(data)

    def transform(self, data):
        properties_feature_matrix = lil_matrix((data['trade_item'].shape[0],
                                                len(self.properties_lut)))

        for i, wid in enumerate(data['trade_item'].id.values):
            for pid, prop in data['trade_item_property'][data['trade_item_property'].item_id == wid].iterrows():
                if prop.property_id in self.properties_lut:
                    # select not null values of a property
                    values = [v for v in [prop.value0,
                                          prop.value1] if v is not None]

                    if len(values) > 0 and self.how == 'mean':
                        values = np.mean(values)
                    elif len(values) == 0 or self.how == 'flag':
                        values = 1

                    properties_feature_matrix[i,
                                              self.properties_lut[prop.property_id]] = values
        return properties_feature_matrix


class Category:
    def __init__(self):
        self.ohe = OneHotEncoder(drop='first')

    def fit_transform(self, data):
        return self.ohe.fit_transform(data['trade_item'].category.values.reshape(-1, 1))

    def transform(self, data):
        return self.ohe.transform(data['trade_item'].category.values.reshape(-1, 1))


class SubCategories:
    def __init__(self):
        self.ohe = OneHotEncoder(drop='first')

    def fit_transform(self, data):
        return self.ohe.fit_transform(data['trade_item'].sub_category.values.reshape(-1, 1))

    def transform(self, data):
        return self.ohe.transform(data['trade_item'].sub_category.values.reshape(-1, 1))


class Rarity:
    def __init__(self):
        pass

    def fit_transform(self, data):
        self.ohe = OneHotEncoder(drop='first')
        return self.ohe.fit_transform(data['trade_item'].rarity.values.reshape(-1, 1))

    def transform(self, data):
        return self.ohe.transform(data['trade_item'].rarity.values.reshape(-1, 1))

# ============================== TARGET FEATURES ===============================
# TODO: custom trade rates based on specific currencies


class Price:
    def __init__(self, market_head=10, outlier_window=3):
        '''
        - outlier_window: int
            Remove trades rate which value is outside the normal distribution window ù
            defined as (mean_value +- standard deviation * window).

        - market_head: int
            select only the top deals based on the exchange rate. Those deals most
            likely are the most representative of the currency exchange rates.
        '''
        self.market_head = market_head
        self.outlier_window = outlier_window

    def fit_transform(self, data, currencies):
        self.currency_set = set(set(currencies.sell_currency.values) &
                                set(currencies.price_currency.values))

        self._extract_exchange_rates(currencies)

        return self.transform(data, currencies)

    def transform(self, data, currencies):
        price = np.zeros((len(data['trade_item']), 1))
        for i, (k, v) in enumerate(data['trade_item'].iterrows()):
            if v.price_currency != 'chaos':
                price[i, 0] = self.c_rates.loc['chaos',
                                               v.price_currency] * v.price_quantity
            else:
                price[i, 0] = v.price_quantity
        return price

    def _extract_exchange_rates(self, currencies):
        self.c_rates = pd.DataFrame(
            index=self.currency_set, columns=self.currency_set)
        currencies['rate'] = currencies.sell_quantity / \
            currencies.price_quantity

        for v1 in self.currency_set:
            for v2 in set(self.currency_set):
                if v1 == v2:
                    value = 1
                else:
                    temp = currencies[(currencies.sell_currency == v1) &
                                      (currencies.price_currency == v2)].copy()
                    temp.sort_values('rate', ascending=False, inplace=True)
                    temp['n_rate'] = temp.rate.apply(lambda y: (
                        y - temp.rate.mean()) / temp.rate.std())
                    temp = temp[(temp.n_rate > -self.outlier_window) &
                                (temp.n_rate < self.outlier_window)].rate
                    value = round(np.mean(temp.head(self.market_head)), 3)

                self.c_rates.loc[v1, v2] = value

    def _map_price(self, y):
        return self.c_rates.loc['chaos', currency] * quantity
