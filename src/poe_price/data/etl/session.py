import time
import logging

from ..session import PSQLSession

log = logging.getLogger(__name__)

TRADE_CURRENCY = ['league', 'sell_currency', 'price_currency',
                  'sell_quantity', 'price_quantity', 'is_stash_price', 'date']

TRADE_ITEM = ['category', 'corrupted', 'duplicated', 'identified', 'ilvl',
              'influence_crusader', 'influence_elder', 'influence_hunter',
              'influence_redeemer', 'influence_shaper', 'influence_warlord',
              'league', 'num_prefixes', 'num_suffixes', 'num_veiled_modifiers',
              'price_currency', 'price_quantity', 'is_stash_price', 'rarity',
              'requirement_dex', 'requirement_int', 'requirement_str',
              'requirement_level', 'sub_category', 'synthesised', 'talisman_tier',
              'date']

TRADE_ITEM_MODIFIER = ['item_id', 'modifier_id', 'value0', 'value1', 'value2']

TRADE_ITEM_SOCKETS = ['item_id', 'socket_group', 'colour']

TRADE_ITEM_PROPERTY = ['item_id', 'property_id', 'value0', 'value1']

ITEM_MODIFIER = ['text', 'type']

ITEM_PROPERTY = ['text']


class ETLSession(PSQLSession):
    def __init__(self, host, database, user, password, debug):
        super().__init__(host, database, user, password)

        # convert items preprocessing index to db index (external)
        self._item_id_lookup = dict()
        self._modifier_id_lookup = dict()
        self._property_id_lookup = dict()

        self._property_cache = dict()
        self._modifier_cache = dict()

        self.debug = debug

    def insert_currency(self, data):
        super().insert_query('trade_currency', TRADE_CURRENCY, data, multiple=True)

    def insert_property_type(self, source_id, data):
        # check whenever the property already exist and get the record index ...
        full_data_property = data['text']
        if full_data_property not in self._property_cache:
            db_id = super().check_record_existance('property_type', data)
            if db_id is not None:
                self._property_cache[full_data_property] = db_id
            else:
                # ... otherwise insert a new record and get the id
                db_id = super().insert_query('property_type', ITEM_PROPERTY, data, return_id=True)
                self._property_cache[full_data_property] = db_id
        else:
            db_id = self._property_cache[full_data_property]

        self._property_id_lookup[source_id] = db_id

    def insert_modifier_type(self, source_id, data):
        # check whenever the property already exist and get the record index ...
        full_data_modifier = data['text'] + data['type']
        if full_data_modifier not in self._modifier_cache:
            db_id = super().check_record_existance('modifier_type', data)
            if db_id is not None:
                self._modifier_cache[full_data_modifier] = db_id
            else:
                # ... otherwise insert a new record and get the id
                db_id = super().insert_query('modifier_type', ITEM_MODIFIER, data, return_id=True)
                self._modifier_cache[full_data_modifier] = db_id
        else:
            db_id = self._modifier_cache[full_data_modifier]
        self._modifier_id_lookup[source_id] = db_id

    def insert_item(self, data):
        # insert item and get id
        new_ids = super().insert_query('trade_item', TRADE_ITEM,
                                       data.values(), multiple=True, return_id=True)

        for final_id, (item_id, item_data) in zip(new_ids, data.items()):
            self._item_id_lookup[item_id] = final_id

    def insert_item_socket(self, data):
        for item_mod in data:
            item_mod['item_id'] = self._item_id_lookup[item_mod['item_id']]

        super().insert_query('trade_item_socket', TRADE_ITEM_SOCKETS, data, multiple=True)

    def insert_item_property(self, data):
        for item_mod in data:
            item_mod['item_id'] = self._item_id_lookup[item_mod['item_id']]
            item_mod['property_id'] = self._property_id_lookup[item_mod['property_id']]

        super().insert_query('trade_item_property', TRADE_ITEM_PROPERTY, data, multiple=True)

    def insert_item_modifier(self, data):
        for item_mod in data:
            item_mod['item_id'] = self._item_id_lookup[item_mod['item_id']]
            item_mod['modifier_id'] = self._modifier_id_lookup[item_mod['modifier_id']]

        super().insert_query('trade_item_modifier', TRADE_ITEM_MODIFIER, data, multiple=True)

    def clean_cache(self):
        self._item_id_lookup = dict()
