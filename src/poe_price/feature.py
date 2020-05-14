import numpy as np
import pandas as pd
from scipy.sparse import lil_matrix, csr_matrix
from sklearn.preprocessing import LabelEncoder, OneHotEncoder


# ============================== COMMON FUNCTIONS ==============================


# ============================= FUNCTION FEATURES ==============================
def corrupted(data):
    return data['items'].corrupted.fillna(False).astype(int).values.reshape(-1,1)

def duplicated(data):
    return data['items']['duplicated'].fillna(False).astype(int).values.reshape(-1,1)

def identified(data):
    return data['items'].identified.fillna(False).astype(int).values.reshape(-1,1)

def suffixes_subcount(data):
    columns = [column for column in data['items'].columns
                      if column in ['num_veiled_mods', 'num_prefixes', 'num_suffixes']]
    return data['items'].loc[:, columns].fillna(0).values

def requirements(data):
    columns = [column for column in data['items'].columns
                      if 'requirement' in column]
    return  data['items'].loc[:, columns].fillna(0).values

def veiled(data, how='flag'):
    '''
    how: 'flag', 'count' or 'both' to extract respectively a binary value,
         count of veiled mods or both of the previous values.
    '''
    data['items'].num_veiled_modifiers.fillna(0, inplace=True)
    if how == 'flag':
        feature = data['items'].num_veiled_modifiers.apply(lambda y: 1
                                                           if y > 0 else 0).values.reshape(-1,1)
    elif how == 'count':
        feature = data['items'].num_veiled_modifiers.values.reshape(-1,1)
    elif how == 'both':
        feature = np.column_stack((veiled(data, how='flag'),
                                   veiled(data, how='count')))
    else:
        raise ValueError()
    return feature

def influences(data):
    columns = [column for column in data['items'].columns if 'influence' in column]

    feature = data['items'].loc[:, columns].fillna(False)
    feature.loc[:, :] = feature.loc[:, :].astype(int)

    return csr_matrix(feature.values)

def sockets(data):
    features = np.zeros((data['items'].shape[0], 7))
    for k, iid in enumerate(data['items'].id.values):
        sockets = data['items_sockets'][data['items_sockets'].item_id == iid]
        scolors = sockets.colour.value_counts()
        features[k, 0] = sockets.shape[0]
        features[k, 1] = scolors['R'] if 'R' in scolors else 0
        features[k, 2] = scolors['G'] if 'G' in scolors else 0
        features[k, 3] = scolors['B'] if 'B' in scolors else 0
        features[k, 4] = scolors['W'] if 'W' in scolors else 0
        features[k, 5] = scolors['A'] if 'A' in scolors else 0
        features[k, 6] = sockets.socket_group.value_counts().iloc[0]
    return csr_matrix(features)

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
            sorted(set(data['items_modifiers'].modifier_id.values)))}

        return self.transform(data)

    def transform(self, data):
        modifiers_feature_matrix = lil_matrix((data['items'].shape[0],
                                               len(self.modifiers_lut)))

        for i, wid in enumerate(data['items'].id.values):
            for pid, mod in data['items_modifiers'] \
                                [data['items_modifiers'].item_id == wid].iterrows():
                if mod.modifier_id in self.modifiers_lut:
                    # select not null values of a modifier
                    values = [v for v in [mod.value0, mod.value1, mod.value2]
                                if ~np.isnan(v)]

                    if len(values) > 0 and self.how == 'mean':
                        values = np.mean(values)
                    elif len(values) == 0 or self.how == 'flag':
                        values = 1

                    modifiers_feature_matrix[i, self.modifiers_lut[mod.modifier_id]] = values

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
            sorted(set(data['items_properties'].property_id.values)))}

        return self.transform(data)

    def transform(self, data):
        properties_feature_matrix = lil_matrix((data['items'].shape[0],
                                               len(self.properties_lut)))

        for i, wid in enumerate(data['items'].id.values):
            for pid, prop in data['items_properties'] \
                                [data['items_properties'].item_id == wid].iterrows():
                if prop.property_id in self.properties_lut:
                    # select not null values of a property
                    values = [v for v in [prop.value0, prop.value1]
                                if ~np.isnan(v)]

                    if len(values) > 0 and self.how == 'mean':
                        values = np.mean(values)
                    elif len(values) == 0 or self.how == 'flag':
                        values = 1

                    properties_feature_matrix[i, self.properties_lut[prop.property_id]] = values
        return properties_feature_matrix

class Category:
    def __init__(self):
        self.ohe = OneHotEncoder()

    def fit_transform(self, data):
        return self.ohe.fit_transform(data['items'].category.values.reshape(-1,1))

    def transform(self, data):
        return self.ohe.transform(data['items'].category.values.reshape(-1,1))

class SubCategories:
    def __init__(self):
        self.ohe = OneHotEncoder()

    def fit_transform(self, data):
        return self.ohe.fit_transform(data['items'].sub_category.values.reshape(-1,1))

    def transform(self, data):
        return self.ohe.transform(data['items'].sub_category.values.reshape(-1,1))

class Rarity:
    def __init__(self):
        pass

    def fit_transform(self, data):
        self.ohe = OneHotEncoder()
        return self.ohe.fit_transform(data['items'].rarity)

    def transform(self, data):
        return self.ohe.transform(data['items'].rarity)

# ============================== TARGET FEATURES ===============================
# TODO: custom trade rates based on specific currencies
class Price:
    def __init__(self, market_head=20, outlier_window=1):
        '''
        outlier_window: remove trades rate which value is outside the normal
                        distribution window defined as
                        (mean_value +- standard deviation * window).

        market_head: select only the top deals based on the exchange rate.
                     Those deals most likely are the most representative of the
                     currency exchange rates.
        '''
        self.market_head = market_head
        self.outlier_window = outlier_window

    def fit_transform(self, data, currencies):
        self._extract_exchange_rates(currencies)

        return self.transform(data, currencies)

    def transform(self, data, currencies):
        price = np.zeros((len(data['items']), 1))
        for i, (k, v) in enumerate(data['items'].iterrows()):
            if v.price_currency != 'chaos':
                price[i, 0] = self.c_rates.loc['chaos', v.price_currency] * v.price_quantity
            else:
                price[i, 0] = v.price_quantity
        return csr_matrix(price)

    def _extract_exchange_rates(self, currencies):
        self.c_rates = pd.DataFrame(index=set(currencies.price_currency.values),
                       columns=set(currencies.price_currency.values))
        currencies['rate'] = currencies.sell_quantity / currencies.price_quantity
        for v1 in currencies:
            for v2 in set(currencies) - set(v1):

                if v1 == 'chaos' or v2 == 'chaos':
                    temp = currencies[(currencies.sell_currency==v1) &
                                    (currencies.price_currency==v2)].copy()
                    temp.sort_values('rate', ascending=False, inplace=True)
                    temp['n_rate'] = temp.rate.apply(lambda y:
                        (y - temp.rate.mean()) / temp.rate.std())
                    temp = temp[(temp.n_rate > -self.outlier_window) &
                                  (temp.n_rate < self.outlier_window)].rate
                    self.c_rates.loc[v1, v2] = round(np.mean(
                        temp.head(self.market_head).rate), 3)

    def _map_price(self, y):
        return self.c_rates.loc['chaos', currency] * quantity
