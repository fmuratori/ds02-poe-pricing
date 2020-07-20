from ..session import PSQLSession

CACHE_PROPERTY = {}
CACHE_MODIFIER = {}

class ETLSession(PSQLSession):
    def __init__(self, host, database, user, password):
        super().__init__(host, database, user, password)

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
