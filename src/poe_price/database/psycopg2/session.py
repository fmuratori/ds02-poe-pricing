import datetime

import psycopg2
import pandas as pd
class PSQLSession:
    def __init__(self, host, database, user, password):
        self.connection = psycopg2.connect(host=host,
                                           database=database,
                                           user=user,
                                           password=password)

    def __enter__(self):
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.cursor.close()
        self.connection.commit()
        self.connection.close()

    def check_record_existance(self, table, data):
        query_text = '''SELECT id FROM {} WHERE {};'''.format(table,
                     self._get_query_elements(data, type='select'))

        self.cursor.execute(query_text)
        result = self.cursor.fetchall()
        return result[0][0] if len(result) > 0 else None

    def insert_query(self, table, data, return_id=False):
        query_text = '''INSERT INTO {}({}) VALUES({})'''.format(table,
                    *self._get_query_elements(data))
        if return_id:
            query_text += ' RETURNING id'
        query_text += ';'

        # print(query_text)
        self.cursor.execute(query_text)

        if return_id:
            return self.cursor.fetchall()[0][0]

    def _get_query_elements(self, data, type='insert'):
        # delete pd.nan values
        deletable = []
        for k in data.keys():
            if pd.isna(data[k]):
                deletable.append(k)
        for k in deletable: del(data[k])

        keys = data.keys()

        values = [str(v) if not isinstance(v, str) and not isinstance(v, datetime.date)
                         else '\'{}\''.format(v.replace('\'', '"'))
                         for v in data.values()]
        if type == 'insert':
            return ', '.join(keys), ', '.join(values)
        elif type == 'select':
            return ' AND '.join(['{}={}'.format(key, value) for key, value in zip(keys, values)])

# ================================= poe_price =================================

CACHE_PROPERTY = {}
CACHE_MODIFIER = {}

class PoePriceDBSession(PSQLSession):
    def __init__(self):
        super().__init__('127.0.0.1', 'poe_price', 'fabio', 'password')

        # convert items preprocessing index to db index (external)
        self._item_id_lookup = dict()
        self._modifier_id_lookup = dict()
        self._property_id_lookup = dict()

    def insert_currency(self, data):
        super().insert_query('trade_currency', data)

    def insert_property_type(self, source_id, data):
        # check whenever the property already exist and get the record index ...
        full_data_property = data['text']
        if full_data_property not in CACHE_PROPERTY:
            db_id = super().check_record_existance('property_type', data)
            if db_id is not None:
                CACHE_PROPERTY[full_data_property] = db_id
            else:
                # ... otherwise insert a new record and get the id
                db_id = super().insert_query('property_type', data, return_id=True)
                CACHE_PROPERTY[full_data_property] = db_id
        else:
            db_id = CACHE_PROPERTY[full_data_property]

        self._property_id_lookup[source_id] = db_id

    def insert_modifier_type(self, source_id, data):
        # check whenever the property already exist and get the record index ...
        full_data_modifier = data['text'] + data['type']
        if full_data_modifier not in CACHE_MODIFIER:
            db_id = super().check_record_existance('modifier_type', data)
            if db_id is not None:
                CACHE_MODIFIER[full_data_modifier] = db_id
            else:
                # ... otherwise insert a new record and get the id
                db_id = super().insert_query('modifier_type', data, return_id=True)
                CACHE_MODIFIER[full_data_modifier] = db_id
        else:
            db_id = CACHE_MODIFIER[full_data_modifier]
        self._modifier_id_lookup[source_id] = db_id

    def insert_item(self, id, data):
        # insert item and get id
        new_id = super().insert_query('trade_item', data, return_id=True)

        self._item_id_lookup[id] = new_id

    def insert_item_socket(self, data):
        data['item_id'] = self._item_id_lookup[data['item_id']]
        super().insert_query('trade_item_socket', data)

    def insert_item_property(self, data):
        data['item_id'] = self._item_id_lookup[data['item_id']]
        data['property_id'] = self._property_id_lookup[data['property_id']]
        super().insert_query('trade_item_property', data)

    def insert_item_modifier(self, data):
        data['item_id'] = self._item_id_lookup[data['item_id']]
        data['modifier_id'] = self._modifier_id_lookup[data['modifier_id']]
        super().insert_query('trade_item_modifier', data)
