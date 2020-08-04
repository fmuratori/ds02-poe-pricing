from .session import PSQLSession


def _get_by_item_category(categories, conn_config, currency_types):
    if currency_types is None:
        currency_types = ['']

    data = {}
    with PSQLSession(conn_config['host'], conn_config['database'],
                     conn_config['user'], conn_config['password']) as session:

        # select items
        if currency_types is None:
            data['trade_item'] = session.query('''
                SELECT * FROM trade_item
                WHERE category IN ('{}');
                '''.format('\', \''''.join(categories)))
        else:
            data['trade_item'] = session.query('''
                SELECT * FROM trade_item
                WHERE category IN ('{}')
                AND price_currency IN ('{}');
                '''.format('\', \''''.join(categories), '\', \''''.join(currency_types)))

        # select items additional data
        data['trade_item_modifier'] = session.query('''
            SELECT tim.* FROM trade_item as ti, trade_item_modifier as tim
            WHERE tim.item_id = ti.id
            AND ti.id IN ({});
            '''.format(', '.join([str(v) for v in data['trade_item'].id.values])))
        data['trade_item_property'] = session.query('''
            SELECT tip.* FROM trade_item as ti, trade_item_property as tip
            WHERE tip.item_id = ti.id
            AND ti.id IN ({});
            '''.format(', '.join([str(v) for v in data['trade_item'].id.values])))
        data['trade_item_socket'] = session.query('''
            SELECT tis.* FROM trade_item as ti, trade_item_socket as tis
            WHERE tis.item_id = ti.id
            AND ti.id IN ({});
            '''.format(', '.join([str(v) for v in data['trade_item'].id.values])))
        data['modifier_type'] = session.query('''
            SELECT mt.* FROM trade_item as ti, trade_item_modifier as tim,
            modifier_type as mt
            WHERE tim.item_id = ti.id
            AND mt.id = tim.modifier_id
            AND ti.id IN ({});
            '''.format(', '.join([str(v) for v in data['trade_item'].id.values])))
        data['property_type'] = session.query('''
            SELECT pt.* FROM trade_item as ti, trade_item_property as tip,
            property_type as pt
            WHERE tip.item_id = ti.id
            AND pt.id = tip.property_id
            AND ti.id IN ({});
            '''.format(', '.join([str(v) for v in data['trade_item'].id.values])))
    return data


def get_jewels(conn_config, currency_types=None):
    return _get_by_item_category(['jewels'], conn_config, currency_types)


def get_armours(conn_config, currency_types=None):
    return _get_by_item_category(['armour'], conn_config, currency_types)


def get_weapons(conn_config, currency_types=None):
    return _get_by_item_category(['weapons'], conn_config, currency_types)


def get_accessories(conn_config, currency_types=None):
    return _get_by_item_category(['accessories'], conn_config, currency_types)


def get_mod_items(conn_config, currency_types=None):
    return _get_by_item_category(['jewels', 'armour', 'weapons', 'accessories'], conn_config, currency_types)


def get_currency(conn_config):
    with PSQLSession(conn_config['host'], conn_config['database'],
                     conn_config['user'], conn_config['password']) as session:
        data = session.query('SELECT * FROM trade_currency')
    return data
