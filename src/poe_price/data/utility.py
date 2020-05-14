import click

from .session import PSQLSession

# TODO: get PSQLSession params from ../config.ini

@click.command()
@click.option("--clean", default=False, help="Clean all db tables")
@click.option("--stats", default=False, help="Show db statistics")
def parse_options(clean, stats):
    with PSQLSession('127.0.0.1', 'poe_price', 'fabio', 'password') as session:
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
