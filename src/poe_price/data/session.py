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

    def query(self, text):
        self.cursor.execute(text)
        data = pd.DataFrame(self.cursor.fetchall(),
                            columns = [desc[0]
                                       for desc in self.cursor.description])
        return data

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