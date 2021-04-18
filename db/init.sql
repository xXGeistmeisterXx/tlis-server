CREATE DATABASE IF NOT EXISTS TLIS;

CREATE TABLE IF NOT EXISTS customers (
	id MEDIUMINT KEY AUTO_INCREMENT,
	number VARCHAR(16),
	first_name VARCHAR(32),
	last_name VARCHAR(32),
	email VARCHAR(64),
	grade TINYINT,
	staff TINYINT(1)
);

CREATE TABLE IF NOT EXISTS techs (
	id MEDIUMINT KEY AUTO_INCREMENT,
	customer_id MEDIUMINT,
	username VARCHAR(32),
	permission TINYINT,
	password BINARY(128),
	salt BINARY(32)
);

CREATE TABLE IF NOT EXISTS assets(
	id MEDIUMINT KEY AUTO_INCREMENT,
	number INT,
	type TINYINT
);

CREATE TABLE IF NOT EXISTS asset_types(
	id MEDIUMINT KEY AUTO_INCREMENT,
	name VARCHAR(32),
	prefix VARCHAR(6),
	max_time_out BIGINT,
	description VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS transactions_out(
	id MEDIUMINT KEY AUTO_INCREMENT,
	type TINYINT,
	asset_id MEDIUMINT,
	customer_id MEDIUMINT,
	tech_id MEDIUMINT,
	time_now BIGINT,
	time_due BIGINT,
	notes VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS  transactions_in(
	id MEDIUMINT KEY,
	type TINYINT,
	tech_id MEDIUMINT,
	time_now BIGINT,
	notes VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS transaction_types(
        id MEDIUMINT KEY AUTO_INCREMENT,
	name VARCHAR(32),
	description VARCHAR(200)
);
