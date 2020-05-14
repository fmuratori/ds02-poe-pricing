from .session import PSQLSession

# TODO: select only latest data
# TODO: get PSQLSession params from ../config.ini

def _get_by_item_category(category):
    data = {}
    with PSQLSession('localhost', 'poe_price', 'fabio', 'password') as session:
        data['items'] = session.query('''
            SELECT * FROM trade_item
            WHERE category = '{}';
            '''.format(category))
        data['items_modifiers'] = session.query('''
            SELECT tim.* FROM trade_item as ti, trade_item_modifier as tim
            WHERE tim.item_id = ti.id
            AND ti.category = '{}';
            '''.format(category))
        data['items_properties'] = session.query('''
            SELECT tip.* FROM trade_item as ti, trade_item_property as tip
            WHERE tip.item_id = ti.id
            AND ti.category = '{}';
            '''.format(category))
        data['items_sockets'] = session.query('''
            SELECT tis.* FROM trade_item as ti, trade_item_socket as tis
            WHERE tis.item_id = ti.id
            AND ti.category = '{}';
            '''.format(category))
        data['modifiers'] = session.query('''
            SELECT tim.* FROM trade_item as ti, trade_item_modifier as tim,
            modifier_type as mt
            WHERE tim.item_id = ti.id
            AND mt.id = tim.modifier_id
            AND ti.category = '{}';
            '''.format(category))
        data['properties'] = session.query('''
            SELECT tip.* FROM trade_item as ti, trade_item_property as tip,
            property_type as pt
            WHERE tip.item_id = ti.id
            AND pt.id = tip.property_id
            AND ti.category = '{}';
            '''.format(category))
    return data

def get_jewels():
    return _get_by_item_category('jewels')

def get_armours():
    return _get_by_item_category('armours')

def get_weapons():
    return _get_by_item_category('weapons')

def get_accessories():
    return _get_by_item_category('accessories')

def get_currency():
    with PSQLSession('localhost', 'poe_price', 'fabio', 'password') as session:
        data = session.query('SELECT * FROM trade_currency')
    return data
