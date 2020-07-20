import click
import configparser

from .session import PSQLSession

# TODO: get PSQLSession params from ../config.ini

@click.command()
@click.argument("connect", default='connect.ini')
@click.option("--clean", default=False, help="Clean all db tables")
@click.option("--stats", default=False, help="Show db statistics")
def parse_options(connect, clean, stats):
    # extract database params from config file
    conn_config = configparser.ConfigParser()
    conn_config.read(connect)
    host = conn_config['postgresql']['host']
    database = conn_config['postgresql']['database']
    user = conn_config['postgresql']['user']
    password = conn_config['postgresql']['password']

    # open database session
    with PSQLSession(host, database, user, password) as session:
        session.cursor.execute('''SELECT table_name
                                  FROM information_schema.tables
                                  WHERE table_type='BASE TABLE'
                                  AND table_schema='public';''')
        tnames = [v[0] for v in session.cursor.fetchall()]

        if clean:
            # drop all connections to the database except the current one
            session.cursor.execute('''
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = 'poe_price'
                AND pid <> pg_backend_pid();''')

            session.cursor.execute('''DELETE FROM trade_item_socket;''')
            session.cursor.execute('''DELETE FROM trade_item_property;''')
            session.cursor.execute('''DELETE FROM trade_item_modifier;''')
            session.cursor.execute('''DELETE FROM trade_item CASCADE;''')
            session.cursor.execute('''DELETE FROM trade_currency;''')
            session.cursor.execute('''DELETE FROM modifier_type;''')
            session.cursor.execute('''DELETE FROM property_type;''')

            # for i in range(3):
            #     print(i)
            #     session.cursor.execute('''DELETE FROM trade_item WHERE id={};'''.format(i))

        if stats:
            for tname in tnames:
                session.cursor.execute('''SELECT COUNT(*) FROM {};'''.format(tname))
                result = session.cursor.fetchall()[0][0]
                print('TABLE {}: {} elements'.format(tname, result))


if __name__ == '__main__':
    parse_options()
