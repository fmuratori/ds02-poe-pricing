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
corrupted BOOLEAN DEFAULT FALSE,
duplicated BOOLEAN DEFAULT FALSE,
identified BOOLEAN DEFAULT FALSE,
ilvl SMALLINT DEFAULT 0,
influence_crusader BOOLEAN DEFAULT FALSE,
influence_elder BOOLEAN DEFAULT FALSE,
influence_hunter BOOLEAN DEFAULT FALSE,
influence_redeemer BOOLEAN DEFAULT FALSE,
influence_shaper BOOLEAN DEFAULT FALSE,
influence_warlord BOOLEAN DEFAULT FALSE,
league VARCHAR(50) NOT NULL,
num_prefixes SMALLINT DEFAULT 0,
num_suffixes SMALLINT DEFAULT 0,
num_veiled_modifiers SMALLINT DEFAULT 0,
price_currency VARCHAR(50) NOT NULL,
price_quantity INTEGER NOT NULL,
is_stash_price BOOLEAN NOT NULL,
rarity VARCHAR(50) NOT NULL,
requirement_dex SMALLINT DEFAULT 0,
requirement_int SMALLINT DEFAULT 0,
requirement_str SMALLINT DEFAULT 0,
requirement_level SMALLINT DEFAULT 0,
sub_category VARCHAR(50) DEFAULT '',
synthesised BOOLEAN DEFAULT FALSE,
talisman_tier SMALLINT DEFAULT 0,
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
