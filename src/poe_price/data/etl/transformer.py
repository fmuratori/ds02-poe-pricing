from threading import Thread
import logging
import time
import re
from datetime import datetime
import pandas as pd

log = logging.getLogger(__name__)

TEMP = []

LEAGUES = ['Harvest']
CURRENCY_DICT = {
    'Chromatic Orb': ['chrom'],
    'Orb of Alteration': ['alt'],
    'Jeweller\'s Orb': ['jewel'],
    'Orb of Chance': ['chance'],
    'Cartographer\'s Chisel': ['chisel', 'cartographer'],
    'Orb of Fusing': ['fusing', 'fuse'],
    'Orb of Alchemy': ['alch'],
    'Orb of Scouring': ['scour'],
    'Blessed Orb': ['blessed'],
    'Chaos Orb': ['chaos'],
    'Orb of Regret': ['regret'],
    'Regal Orb': ['regal'],
    'Gemcutter\'s Prism': ['gcp', 'gemcutter'],
    'Divine Orb': ['divine'],
    'Exalted Orb': ['exalted', 'exa'],
    'Mirror of Kalandra': ['mirror']}
INV_CURRENCY_DICT = {value: k for k, values in CURRENCY_DICT.items()
                     for value in values}

ITEM_CATEGORY = ['accessories', 'armour', 'jewels', 'weapons', 'currency']

FRAME_TYPES = {0: 'normal', 1: 'magic', 2: 'rare', 3: 'unique', 4: 'gem', 5: 'currency',
               6: 'divination card', 7: 'quest item', 8: 'prophecy', 9: 'relic'}

CURRENCY_COLUMNS = ['league', 'price_currency', 'price_quantity', 'is_stash_price', 'sell_quantity',
                    'sell_currency', 'date']
MITEMS_COLUMNS = ['category', 'corrupted', 'duplicated', 'identified', 'ilvl',
                  'influence_crusader', 'influence_elder', 'influence_hunter',
                  'influence_redeemer', 'influence_shaper', 'influence_warlord',
                  'league', 'num_prefixes', 'num_suffixes', 'num_veiled_modifiers',
                  'price_currency', 'price_quantity', 'is_stash_price', 'rarity',
                  'requirement_dex', 'requirement_int', 'requirement_level',
                  'requirement_str', 'sub_category', 'synthesised', 'talisman_tier',
                  'date']


def get_items(data, df=True):
    items = []
    for stash in data['stashes']:
        if stash['public']:
            for item in stash['items']:
                item['league'] = stash['league']
                item['stash_note'] = stash['stash']
                items.append(item)
    if df:
        items = pd.DataFrame(items)
    return items

# extract new data from existing data


def extract_item_category(items):
    items['sub_category'] = items.extended.apply(lambda y: ' '.join(y['subcategories'])
                                                 if 'subcategories' in y else None)
    items['category'] = items.extended.apply(lambda y: y['category'])
    return items


def extract_item_price(items, use_stash_price=False):
    prices = []
    for k, v in items.iterrows():
        # try to extract item price
        price = (*extract_string_price(v.note), False)

        # if item price is undefined, extract global stash price
        if price is (None, None, None, False) and use_stash_price:
            price = (*extract_string_price(v.stash_note), True)
        prices.append(price)

    (items['price_currency'], items['price_quantity'],
     items['sell_quantity'], items['is_stash_price']) = zip(*prices)
    return items


def extract_string_price(string):
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
                sellingStackSize = 1

            return currency, quantity, sellingStackSize
    except TypeError:
        # no match found
        pass
    return (None, None, None)

# filter out unwanted rows


def filter_item_category(items, categories):
    if 'jewels' in categories:
        items = items[~((items.category == 'jewels') &
                        (items.sub_category == 'cluster'))]

    if 'currency' in categories:
        items = items[~((items.category == 'currency') & (
            items.sub_category.isin(['fossil', 'seed primalseed', 'seed vividseed', 'piece'])))]

    return items[items.category.isin(categories)]


def filter_item_league(items, leagues):
    return items[items.league.isin(leagues)]


def filter_item_price(items):
    items['price_currency'] = items.price_currency.apply(
        lambda y: y.lower() if y is not None else None)

    items = items[(items.price_currency.notna()) &
                  (items.price_quantity.notna()) &
                  (items.sell_quantity.notna()) &
                  (items.price_currency.isin(INV_CURRENCY_DICT)) &
                  (items.price_quantity > 0) &
                  (items.sell_quantity > 0)]

    # UNTESTED
    # convert rarely used currency identifier to preferable identifier
    target_condition = items.price_currency.isin(
        ['cartographer', 'fuse', 'gemcutter', 'exa'])
    items[target_condition].price_currency = items[target_condition].price_currency.apply(
        lambda y: CURRENCY_DICT[INV_CURRENCY_DICT[y]][0])

    return items


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
                        prop_index = mitems_props_vocabulary.index(
                            generic_prop)
                    except:
                        mitems_props_vocabulary.append(generic_prop)
                        prop_index = len(mitems_props_vocabulary) - 1
                    item_prop['property_id'] = prop_index
                    for i, v in enumerate(prop['values'][0][0].split('-')):
                        try:
                            item_prop['value{}'.format(i)] = float(
                                re.sub('(\+|-|%)', '', v))
                        except:
                            break
                    mitems_props.append(item_prop)
    mitems_props = pd.DataFrame(mitems_props)
    mitems_props_vocabulary = pd.DataFrame(
        mitems_props_vocabulary, columns=['text'])
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
                        mod_index = mitems_mods_vocabulary.index(
                            (generic_mod, mod_type))
                    except:
                        mitems_mods_vocabulary.append((generic_mod, mod_type))
                        mod_index = len(mitems_mods_vocabulary) - 1
                    item_mod['modifier_id'] = mod_index
                    for i, v in enumerate(re.findall('\d+', mod)):
                        item_mod['value{}'.format(i)] = int(v)
                    mitems_mods.append(item_mod)
    mitems_mods = pd.DataFrame(mitems_mods)
    mitems_mods_vocabulary = pd.DataFrame(
        mitems_mods_vocabulary, columns=['text', 'type'])
    return mitems_mods, mitems_mods_vocabulary

############################### HIGH LEVEL TRANSFORMATION ###############################


def filter_json(content):
    for i, stash in enumerate(content['stashes']):
        if stash['league'] not in LEAGUES or not stash['public']:
            del(content['stashes'][i])
    return content


def extract_items(content):

    items = get_items(content)
    items['date'] = content['datetime']

    items = filter_item_league(items, LEAGUES)
    items = extract_item_category(items)

    items = filter_item_category(items, ITEM_CATEGORY)
    items = extract_item_price(items, use_stash_price=True)
    items = filter_item_price(items)
    return items


def extract_currencies(items):
    currency = items[items.category == 'currency'].copy()
    currency['sell_currency'] = currency.extended.apply(lambda y:
                                                        CURRENCY_DICT[y['baseType']][0]
                                                        if y['baseType'] in CURRENCY_DICT else None)
    currency = currency[currency.sell_currency.notna()]
    currency.drop(columns=[v for v in currency.columns
                           if v not in CURRENCY_COLUMNS],
                  inplace=True, errors='ignore')
    return currency


def extract_mod_items(items):
    mitems = items[items.category.isin(
        ['jewels', 'armour', 'weapons', 'accessories'])].copy()

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
            mitems_influences = mitems['influences'].apply(
                lambda y: y if isinstance(y, dict) else {})
            mitems_influences = pd.DataFrame(mitems_influences.to_list(),
                                             index=mitems_influences.index)
            mitems_influences.columns = ['influence_{}'.format(v)
                                         for v in mitems_influences.columns]

            mitems = pd.merge(mitems, mitems_influences,
                              left_index=True, right_index=True, how='left')

        if 'properties' in mitems:
            mitems_prop, mitems_prop_voc = mitems_prop_formatting(mitems, [
                                                                  'properties'])

        if any([v in mitems for v in ['craftedMods', 'enchantMods',
                                      'explicitMods', 'implicitMods']]):
            mitems_mods, mitems_mods_voc = mitems_mod_formatting(mitems,
                                                                 ['craftedMods', 'enchantMods',
                                                                  'explicitMods', 'implicitMods'])

        if 'requirements' in mitems:
            mitems_req = mitems['requirements'].apply(lambda y: {req['name']: int(req['values'][0][0])
                                                                 for req in y}
                                                      if isinstance(y, list) else {})
            mitems_req = pd.DataFrame(
                mitems_req.to_list(), index=mitems_req.index)
            mitems_req.columns = ['requirement_{}'.format(col_name.lower())
                                  for col_name in mitems_req.columns]
            if 'requirement_strength' in mitems_req:
                mitems_req.loc[mitems_req.requirement_strength.notna(), 'requirement_str'] = \
                    mitems_req[mitems_req.requirement_strength.notna()
                               ].requirement_strength.values
            if 'requirement_dexterity' in mitems_req:
                mitems_req.loc[mitems_req.requirement_dexterity.notna(), 'requirement_dex'] = \
                    mitems_req[mitems_req.requirement_dexterity.notna(
                    )].requirement_dexterity.values
            if 'requirement_intelligence' in mitems_req:
                mitems_req.loc[mitems_req.requirement_intelligence.notna(), 'requirement_int'] = \
                    mitems_req[mitems_req.requirement_intelligence.notna(
                    )].requirement_intelligence.values
            mitems_req.drop(columns=['requirement_strength', 'requirement_dexterity',
                                     'requirement_intelligence'], inplace=True, errors='ignore')
            mitems = pd.merge(mitems, mitems_req,
                              left_index=True, right_index=True, how='left')

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
            mitems_sockets.drop(
                columns=['attr', 'sColour', 'group'], inplace=True)

        if 'veiledMods' in mitems:
            mitems['num_veiled_modifiers'] = mitems.veiledMods.apply(
                lambda y: len(y) if isinstance(y, list) else 0)

        if 'talismanTier' in mitems:
            mitems['talisman_tier'] = mitems['talismanTier']
            del(mitems['talismanTier'])

        mitems.drop(columns=[v for v in mitems.columns
                             if v not in MITEMS_COLUMNS],
                    inplace=True, errors='ignore')

        return mitems, mitems_sockets, mitems_prop, mitems_prop_voc, mitems_mods, mitems_mods_voc
    else:
        return None, None, None, None, None, None
