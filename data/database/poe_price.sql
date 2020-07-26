CREATE TABLE trade_currency(
id SERIAL PRIMARY KEY,
league VARCHAR(30) NOT NULL,
sell_currency VARCHAR (50) NOT NULL,
price_currency VARCHAR (50) NOT NULL,
sell_quantity REAL NOT NULL,
price_quantity REAL NOT NULL,
is_stash_price BOOLEAN NOT NULL,
date varchar(50) NOT NULL);

CREATE TABLE trade_item (
id SERIAL PRIMARY KEY,
category VARCHAR(50) NOT NULL,
corrupted BOOLEAN,
duplicated BOOLEAN,
identified BOOLEAN,
ilvl SMALLINT,
influence_crusader BOOLEAN,
influence_elder BOOLEAN,
influence_hunter BOOLEAN,
influence_redeemer BOOLEAN,
influence_shaper BOOLEAN,
influence_warlord BOOLEAN,
league VARCHAR(50) NOT NULL,
num_prefixes SMALLINT,
num_suffixes SMALLINT,
num_veiled_modifiers SMALLINT,
price_currency VARCHAR(50) NOT NULL,
price_quantity INTEGER NOT NULL,
is_stash_price BOOLEAN NOT NULL,
rarity VARCHAR(50) NOT NULL,
requirement_dex SMALLINT,
requirement_int SMALLINT,
requirement_str SMALLINT,
requirement_level SMALLINT,
sub_category VARCHAR(50),
synthesised BOOLEAN,
talisman_tier SMALLINT,
date varchar(50) NOT NULL);

CREATE TABLE modifier_type(
id SERIAL PRIMARY KEY,
text TEXT NOT NULL,
type VARCHAR(50) NOT NULL);

CREATE TABLE property_type(
id SERIAL PRIMARY KEY,
text TEXT NOT NULL);

CREATE TABLE trade_item_modifier(
id SERIAL PRIMARY KEY,
item_id INTEGER REFERENCES trade_item(id),
modifier_id INTEGER REFERENCES modifier_type(id),
value0 REAL,
value1 REAL,
value2 REAL);

CREATE TABLE trade_item_property(
id SERIAL PRIMARY KEY,
item_id INTEGER REFERENCES trade_item(id),
property_id INTEGER REFERENCES property_type(id),
value0 REAL,
value1 REAL);

CREATE TABLE trade_item_socket(
id SERIAL PRIMARY KEY,
item_id INTEGER REFERENCES trade_item(id),
socket_group SMALLINT NOT NULL,
colour VARCHAR(1) NOT NULL);
