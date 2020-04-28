def get_jewels():
    return session.query(Item).filter(Item.category=='jewels').all()

def get_weapons():
    return session.query(Item).filter(Item.category=='weapons').all()

def get_armour():
    return session.query(Item).filter(Item.category=='armour').all()

def get_currency():
    return session.query(Currency).all()

def get_accessories():
    return session.query(Item).filter(Item.category=='accessories').all()
