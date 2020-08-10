import datetime

import psycopg2
import pandas as pd


class PSQLSession:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    def __enter__(self):
        self.connection = psycopg2.connect(host=self.host,
                                           database=self.database,
                                           user=self.user,
                                           password=self.password)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.cursor.close()
        self.connection.commit()
        self.connection.close()

    def query(self, text):
        self.cursor.execute(text)
        data = pd.DataFrame(self.cursor.fetchall(),
                            columns=[desc[0]
                                     for desc in self.cursor.description])
        return data

    def check_record_existance(self, table, data):
        query_text = '''SELECT id FROM {} WHERE {};'''.format(table,
                                                              ' AND '.join(self.to_string_dict(data)))

        # print(query_text)
        self.cursor.execute(query_text)
        result = self.cursor.fetchall()
        return result[0][0] if len(result) > 0 else None

    def insert_query(self, table, columns, data, return_id=False, multiple=False):
        if multiple:
            query_text = '''INSERT INTO {}({}) VALUES {}'''.format(table, ', '.join(columns),
                                                                   '(' + '), ('.join([self.to_string_values(v, columns) for v in data]) + ')')
        else:
            query_text = '''INSERT INTO {}({}) VALUES {}'''.format(table, ', '.join(columns),
                                                                   '(' + self.to_string_values(data, columns) + ')')
        if return_id:
            query_text += ' RETURNING id'

        query_text += ';'

        # print(query_text)
        self.cursor.execute(query_text)

        if return_id:
            v = [id[0] for id in self.cursor.fetchall()]
            return v if multiple else v[0]

    def _get_query_elements(self, data, type='insert'):
        # delete pd.nan values
        deletable = []
        for k in data.keys():
            if pd.isna(data[k]):
                deletable.append(k)
        for k in deletable:
            del(data[k])

        keys = data.keys()

        values = [str(v) if not isinstance(v, str) and not isinstance(v, datetime.date)
                  else '\'{}\''.format(v.replace('\'', '"'))
                  for v in data.values()]
        if type == 'insert':
            return ', '.join(keys), ', '.join(values)
        elif type == 'select':
            return ' AND '.join(['{}={}'.format(key, value) for key, value in zip(keys, values)])

    def to_string_values(self, data, columns):
        output = []
        for col_name in columns:
            if col_name in data:
                # none value
                if data[col_name] is None or pd.isna(data[col_name]):
                    v = 'NULL'
                elif not isinstance(data[col_name], str):   # numeric value
                    v = str(data[col_name])
                else:                                       # string value
                    v = '\'{}\''.format(data[col_name].replace('\'', '"'))
            else:
                v = 'NULL'
            output.append(v)
        return ', '.join(output)

    def to_string_dict(self, data):
        return ['{}={}'.format(key, str(v)
                               if not isinstance(value, str)
                               else '\'{}\''.format(value.replace('\'', '"')))
                for key, value in data.items()]
