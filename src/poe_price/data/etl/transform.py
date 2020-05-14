from threading import Thread
import logging
import time
import re

import pandas as pd

log = logging.getLogger(__name__)

TEMP = []

CURRENCY_KEY = ['alt', 'fuse', 'alch', 'chaos', 'gcp', 'exa', 'chrom', 'jew',
                'chance', 'chisel', 'scour', 'blessed', 'regret', 'regal', 'divine',
                'vaal', 'silver']
CURRENCY_NAME = ['Orb of Alteration', 'Orb of Fusing', 'Orb of Alchemy', 'Chaos Orb',
                 'Gemcutter\'s Prism', 'Exalted Orb', 'Chromatic Orb', 'Jeweller\'s Orb',
                 'Orb of Chance', 'Cartographer\'s Chisel', 'Orb of Scouring',
                 'Blessed Orb', 'Orb of Regret', 'Regal Orb', 'Divine Orb', 'Vaal Orb',
                 'Silver Coin']
FRAME_TYPES = {0: 'normal', 1: 'magic', 2:'rare', 3: 'unique', 4: 'gem', 5: 'currency',
               6: 'divination card', 7: 'quest item', 8: 'prophecy', 9: 'relic'}
CURRENCY_COLUMNS = ['league', 'price_currency', 'price_quantity', 'sell_quantity',
                    'sell_currency', 'date']
MITEMS_COLUMNS = ['category', 'corrupted', 'duplicated', 'identified', 'ilvl',
                  'influence_crusader', 'influence_elder', 'influence_hunter',
                  'influence_redeemer', 'influence_shaper', 'influence_warlord',
                  'league', 'num_prefixes', 'num_suffixes', 'num_veiled_modifiers',
                  'price_currency', 'price_quantity', 'rarity',
                  'requirement_dex', 'requirement_int', 'requirement_level',
                  'requirement_str', 'sub_category', 'synthesised', 'talisman_tier',
                  'date']

def get_items(data, categories):
    items = []
    for stash in data['stashes']:
        if stash['public']:
            for item in stash['items']:
                item['league'] = stash['league']
                item['stash_note'] = stash['stash']

                if item['extended']['category'] in categories:
                    items.append(item)
    return items

def get_string_price(string):
    try:
        if re.match('(~price|~b/o)\s\d+(\.\d+)?(/\d+(\.\d+)?)?\s\w+', string) is not None:
            tokens = string.split(' ')
            currency, quantity = tokens[2], tokens[1]
            if re.match('\d+((\.|/)\d+)?/\d+((\.|/)\d+)?', quantity):
                quantity, sellingStackSize = quantity.split('/')
                quantity = round(float(quantity), 2)
                sellingStackSize = round(float(sellingStackSize), 2)
            else:
                quantity = round(float(quantity), 2)
                sellingStackSize = None
            # check if currency and quantity are allowed values
            if currency in CURRENCY_KEY and quantity != 0:
                return currency, quantity, sellingStackSize
    except TypeError:
        # no match found
        pass
    return None, None, None

def filter_currency(items):
    currency = items[items.category=='currency'].copy()
    if len(currency) > 0:
        currency['sell_currency'] = currency.extended.apply(lambda y:
            CURRENCY_KEY[CURRENCY_NAME.index(y['baseType'])]
            if y['baseType'] in CURRENCY_NAME else None)
        currency.drop(index = currency[(currency.sell_currency.isna()) |
                                       (currency.sell_currency == currency.price_currency)].index, inplace=True)

        currency.drop(columns = [v for v in currency.columns
                                            if v not in CURRENCY_COLUMNS],
                                 inplace = True, errors='ignore')
        currency.sell_quantity.fillna(1, inplace=True)
        return currency
    return None

def filter_mitems(items):
    mitems = items[items.category.isin(['jewels', 'armour', 'weapons', 'accessories'])].copy()

    if len(mitems) > 0:
        mitems_sockets = None
        mitems_mods, mitems_mods_voc = None, None
        mitems_prop, mitems_prop_voc = None, None

        if 'frameType' in mitems:
            mitems['rarity'] = mitems.frameType.apply(lambda y: FRAME_TYPES[y])
            mitems = mitems[(mitems.rarity.isin(['normal', 'magic', 'rare']))]

        if 'extended' in mitems:
            mitems['num_prefixes'] = mitems.extended.apply(lambda y: y['prefixes']
                                                        if 'prefixes' in y else None)
            mitems['num_suffixes'] = mitems.extended.apply(lambda y: y['suffixes']
                                                        if 'suffixes' in y else None)

        if 'influences' in mitems:
            mitems_influences = mitems['influences'].apply(lambda y: y if isinstance(y, dict) else {})
            mitems_influences = pd.DataFrame(mitems_influences.to_list(),
                                             index=mitems_influences.index)
            mitems_influences.columns = ['influence_{}'.format(v)
                                         for v in mitems_influences.columns]
            mitems = pd.merge(mitems, mitems_influences, left_index=True, right_index=True, how='left')

        if 'properties' in mitems:
            mitems_prop, mitems_prop_voc = mitems_prop_formatting(mitems, ['properties'])

        if any([v in mitems for v in ['craftedMods', 'enchantMods',
                                      'explicitMods', 'implicitMods']]):
            mitems_mods, mitems_mods_voc = mitems_mod_formatting(mitems,
                                                                 ['craftedMods', 'enchantMods',
                                                                  'explicitMods', 'implicitMods'])

        if 'requirements' in mitems:
            mitems_req = mitems['requirements'].apply(lambda y: {req['name']: int(req['values'][0][0])
                                                                 for req in y}
                                                                if isinstance(y, list) else {})
            mitems_req = pd.DataFrame(mitems_req.to_list(), index=mitems_req.index)
            mitems_req.columns = ['requirement_{}'.format(col_name.lower())
                                  for col_name in mitems_req.columns]
            if 'requirement_strength' in mitems_req:
                mitems_req.loc[mitems_req.requirement_strength.notna(), 'requirement_str'] = \
                    mitems_req[mitems_req.requirement_strength.notna()].requirement_strength.values
            if 'requirement_dexterity' in mitems_req:
                mitems_req.loc[mitems_req.requirement_dexterity.notna(), 'requirement_dex'] = \
                    mitems_req[mitems_req.requirement_dexterity.notna()].requirement_dexterity.values
            if 'requirement_intelligence' in mitems_req:
                mitems_req.loc[mitems_req.requirement_intelligence.notna(), 'requirement_int'] = \
                    mitems_req[mitems_req.requirement_intelligence.notna()].requirement_intelligence.values
            mitems_req.drop(columns=['requirement_strength', 'requirement_dexterity',
                                     'requirement_intelligence'], inplace=True, errors='ignore')
            mitems = pd.merge(mitems, mitems_req, left_index=True, right_index=True, how='left')

        # split mitems socket column into separate dataframe
        if 'sockets' in mitems:
            for k, v in mitems.iterrows():
                item_sockets = v['sockets']
                if isinstance(item_sockets, list):
                    for socket in item_sockets:
                        socket['item_id'] = k
            mitems_sockets = pd.DataFrame([socket
                                           for sockets in mitems[mitems.sockets.notna()].sockets.to_list()
                                           for socket in sockets])
            mitems_sockets['colour'] = mitems_sockets['sColour']
            mitems_sockets['socket_group'] = mitems_sockets['group']
            mitems_sockets.drop(columns=['attr', 'sColour', 'group'], inplace=True)

        if 'veiledMods' in mitems:
            mitems['num_veiled_modifiers'] = mitems.veiledMods.apply(lambda y: len(y) if isinstance(y, list) else 0)

        if 'talismanTier' in mitems:
            mitems['talisman_tier'] = mitems['talismanTier']
            del(mitems['talismanTier'])

        mitems.drop(columns = [v for v in mitems.columns
                                    if v not in MITEMS_COLUMNS],
                             inplace=True, errors='ignore')

        return mitems, mitems_sockets, mitems_prop, mitems_prop_voc, mitems_mods, mitems_mods_voc
    else:
        return None, None, None, None, None, None

def mitems_prop_formatting(mitems, target_props):
    mitems_props_vocabulary = []
    mitems_props = []

    t1 = []
    for k, v in mitems.iterrows():
        for target_prop in target_props:
            if isinstance(v[target_prop], list):
                for prop in [p for p in v[target_prop] if len(p['values']) > 0]:
                    item_prop = dict()
                    item_prop['item_id'] = k
                    generic_prop = prop['name']
                    try:
                        prop_index = mitems_props_vocabulary.index(generic_prop)
                    except:
                        mitems_props_vocabulary.append(generic_prop)
                        prop_index = len(mitems_props_vocabulary) - 1
                    item_prop['property_id'] = prop_index
                    for i, v in enumerate(prop['values'][0][0].split('-')):
                        try:
                            item_prop['value{}'.format(i)] = float(re.sub('(\+|-|%)', '', v))
                        except:
                            break
                    mitems_props.append(item_prop)
    mitems_props = pd.DataFrame(mitems_props)
    mitems_props_vocabulary = pd.DataFrame(mitems_props_vocabulary, columns=['text'])
    return mitems_props, mitems_props_vocabulary

def mitems_mod_formatting(mitems, mod_types):
    mitems_mods_vocabulary = []
    mitems_mods = []
    for k, item in mitems.iterrows():
        for mod_type in mod_types:
            if mod_type in item and isinstance(item[mod_type], list):
                for mod in item[mod_type]:
                    item_mod = dict()
                    item_mod['item_id'] = k
                    generic_mod = re.sub('\d+', '#', mod)
                    try:
                        mod_index = mitems_mods_vocabulary.index((generic_mod, mod_type))
                    except:
                        mitems_mods_vocabulary.append((generic_mod, mod_type))
                        mod_index = len(mitems_mods_vocabulary) - 1
                    item_mod['modifier_id'] = mod_index
                    for i, v in enumerate(re.findall('\d+', mod)):
                        item_mod['value{}'.format(i)] = int(v)
                    mitems_mods.append(item_mod)
    mitems_mods = pd.DataFrame(mitems_mods)
    mitems_mods_vocabulary = pd.DataFrame(mitems_mods_vocabulary, columns=['text', 'type'])
    return mitems_mods, mitems_mods_vocabulary


class Transformer(Thread):
    '''
    Basic stashes handler procedure. This class simply save stashes data
    as json files with little to none processing to the source data.
    '''
    def __init__(self, u_cond, p_cond, u_list, p_list, config):
        Thread.__init__(self)

        self.u_cond = u_cond
        self.p_cond = p_cond
        self.u_list = u_list
        self.p_list = p_list
        self.config = config['TRANSFORM']

        # set the run method as one of the available policies
        exec('self.policy = self.{}'.format(self.config['TRANSFORM_POLICY']))

        log.info('[T] - Initialized transformer thread. Policy: {}'.format(self.config['TRANSFORM_POLICY']))

    def run(self):
        while True:
            # pick an element fron the unprocessed data list
            elem = None
            with self.u_cond:
                # wait for new data to be processed
                self.u_cond.wait_for(self._checkUnprocessedCond)

                elem = self.u_list.pop(0)
                u_list_size = len(self.u_list)

            # execute data transformation corresponding to the policy selected in
            # the class constructor

            a = time.time()
            elem = self.policy(*elem)
            b = time.time()

            with self.p_cond:
                # save data into a syncronized list for processed data ready to be serialized
                self.p_list.append(elem)
                # wake up other threads waiting for new data to process
                self.p_cond.notify_all()

                p_list_size = len(self.p_list)

            log.info('[T] - Stashes processed in {} seconds.\tU_LIST_SIZE: {}\tP_LIST_SIZE: {}'.format(round(b-a, 2), u_list_size, p_list_size))

    def _checkUnprocessedCond(self):
        with self.u_cond:
            return len(self.u_list) > 0

    def simpleTransformer(self, curr_nci, content, dtime):
        for i, stash in enumerate(content['stashes']):
            if stash['league'] != self.config['LEAGUE'] or not stash['public']:
                del(content['stashes'][i])
                content['datetime'] = dtime.strftime('%m/%d/%Y')
        return curr_nci, content

    def dbTransformer(self, curr_nci, content, dtime):
        categories = self.config['categories'].split(', ')

        items = pd.DataFrame(get_items(content, categories))
        items['date'] = dtime.strftime("%m/%d/%Y")

        # filter unwanted league items
        items = items[items.league == self.config['LEAGUE']]
        # extract items category and subcategory
        items['sub_category'] = items.extended.apply(lambda y: ' '.join(y['subcategories'])
                                                    if 'subcategories' in y else None)
        items['category'] = items.extended.apply(lambda y: y['category'])
        items.drop(index=items[((items.sub_category=='cluster') &
                               (items.category=='jewels'))].index, inplace=True)

        # get items price
        price = []
        for k, v in items.iterrows():
            price.append(get_string_price(v.note))
        (items['price_currency'], items['price_quantity'], items['sell_quantity']) = zip(*price)
        items = items[(items.price_currency.notna()) & (items.price_quantity>0)]

        # split items by category based on wanted categories
        currency = filter_currency(items)

        mitems, mitems_sockets, mitems_prop, mitems_prop_voc, mitems_mods, \
                mitems_mods_voc = filter_mitems(items)

        return curr_nci, currency, mitems, mitems_sockets, mitems_prop, mitems_prop_voc, mitems_mods, \
                mitems_mods_voc
