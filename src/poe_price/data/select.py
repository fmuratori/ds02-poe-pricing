from .session import PSQLSession

def _get_by_item_category(category, conn_config):
    data = {}
    with PSQLSession(conn_config['host'], conn_config['database'], 
                     conn_config['user'], conn_config['password']) as session:
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

def get_jewels(conn_config):
    return _get_by_item_category('jewels', conn_config)

def get_armours(conn_config):
    return _get_by_item_category('armour', conn_config)

def get_weapons(conn_config):
    return _get_by_item_category('weapons', conn_config)

def get_accessories(conn_config):
    return _get_by_item_category('accessories', conn_config)

def get_currency(conn_config):
    with PSQLSession(conn_config['host'], conn_config['database'], 
                     conn_config['user'], conn_config['password']) as session:
        data = session.query('SELECT * FROM trade_currency')
    return data
