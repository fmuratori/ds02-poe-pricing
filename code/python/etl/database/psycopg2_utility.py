import logging
import datetime

import psycopg2
import pandas as pd
import click

# logging utility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
log = logging.getLogger(__name__)

CACHE_PROPERTY = {}
CACHE_MODIFIER = {}

class PoeTradeDBSession:
    def __init__(self):
        self.connection = psycopg2.connect(host='localhost',
                                           database='poe_price',
                                           user='fabio',
                                           password='password')

        # convert items preprocessing index to db index (external)
        self._item_id_lookup = dict()
        self._modifier_id_lookup = dict()
        self._property_id_lookup = dict()

    def __enter__(self):
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.cursor.close()
        self.connection.commit()
        self.connection.close()

    def insert_currency(self, data):
        self._insert_query('trade_currency', data)

    def insert_property_type(self, source_id, data):
        # check whenever the property already exist and get the record index ...
        full_data_property = data['text']
        if full_data_property not in CACHE_PROPERTY:
            db_id = self._check_record_existance('property_type', data)
            if db_id is not None:
                CACHE_PROPERTY[full_data_property] = db_id
            else:
                # ... otherwise insert a new record and get the id
                db_id = self._insert_query('property_type', data, return_id=True)
                CACHE_PROPERTY[full_data_property] = db_id
        else:
            db_id = CACHE_PROPERTY[full_data_property]

        self._property_id_lookup[source_id] = db_id

    def insert_modifier_type(self, source_id, data):
        # check whenever the property already exist and get the record index ...
        full_data_modifier = data['text'] + data['type']
        if full_data_modifier not in CACHE_MODIFIER:
            db_id = self._check_record_existance('modifier_type', data)
            if db_id is not None:
                CACHE_MODIFIER[full_data_modifier] = db_id
            else:
                # ... otherwise insert a new record and get the id
                db_id = self._insert_query('modifier_type', data, return_id=True)
                CACHE_MODIFIER[full_data_modifier] = db_id
        else:
            db_id = CACHE_MODIFIER[full_data_modifier]
        self._modifier_id_lookup[source_id] = db_id

    def insert_item(self, id, data):
        # insert item and get id
        new_id = self._insert_query('trade_item', data, return_id=True)

        self._item_id_lookup[id] = new_id

    def insert_item_socket(self, data):
        data['item_id'] = self._item_id_lookup[data['item_id']]
        self._insert_query('trade_item_socket', data)

    def insert_item_property(self, data):
        data['item_id'] = self._item_id_lookup[data['item_id']]
        data['property_id'] = self._property_id_lookup[data['property_id']]
        self._insert_query('trade_item_property', data)

    def insert_item_modifier(self, data):
        data['item_id'] = self._item_id_lookup[data['item_id']]
        data['modifier_id'] = self._modifier_id_lookup[data['modifier_id']]
        self._insert_query('trade_item_modifier', data)

    def _check_record_existance(self, table, data):
        query_text = '''SELECT id FROM {} WHERE {};'''.format(table,
                     self._get_query_elements(data, type='select'))

        self.cursor.execute(query_text)
        result = self.cursor.fetchall()
        return result[0][0] if len(result) > 0 else None

    def _insert_query(self, table, data, return_id=False):
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

@click.command()
@click.option("--clean", default=False, help="Clean all db tables")
@click.option("--stats", default=False, help="Show db statistics")
def parse_options(clean, stats):
    with PoeTradeDBSession() as session:
        session.cursor.execute('''SELECT table_name
                                  FROM information_schema.tables
                                  WHERE table_type='BASE TABLE'
                                  AND table_schema='public';''')
        tnames = [v[0] for v in session.cursor.fetchall()]

        if clean:
            session.cursor.execute('''DELETE FROM trade_item_socket;''')
            session.cursor.execute('''DELETE FROM trade_item_property;''')
            session.cursor.execute('''DELETE FROM trade_item_modifier;''')
            session.cursor.execute('''DELETE FROM trade_item;''')
            session.cursor.execute('''DELETE FROM trade_currency;''')
            session.cursor.execute('''DELETE FROM modifier_type;''')
            session.cursor.execute('''DELETE FROM property_type;''')

        if stats:
            for tname in tnames:
                session.cursor.execute('''SELECT COUNT(*) FROM {};'''.format(tname))
                result = session.cursor.fetchall()[0][0]
                print('TABLE {}: {} elements'.format(tname, result))


if __name__ == '__main__':
    parse_options()
