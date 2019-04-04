DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS users;

CREATE TABLE messages(
	id SERIAL,
	sender VARCHAR(256) NOT NULL,
	receiver VARCHAR(256) NOT NUll,
	text_content VARCHAR(256) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE users(
	id SERIAL,
	username VARCHAR(256) NOT NULL UNIQUE,
	email VARCHAR(256) NOT NULL UNIQUE,
	password VARCHAR(256) NOT NULL,
	logged BOOLEAN DEFAULT FALSE,
	auth_token VARCHAR(40) NOT NULL UNIQUE,
	PRIMARY KEY (id)
);
