DROP TYPE IF EXISTS TITLE CASCADE;
CREATE TYPE TITLE AS ENUM ('CREATOR', 'ADMIN', 'MEMBER');

DROP TYPE IF EXISTS VISIBILITY CASCADE;
CREATE TYPE VISIBILITY AS ENUM ('PUBLIC', 'PRIVATE');

DROP TABLE IF EXISTS clients CASCADE;
CREATE TABLE clients(
  id SERIAL,
  PRIMARY KEY (id)
);

DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users(
	id INTEGER NOT NULL UNIQUE,
	username VARCHAR(256) NOT NULL UNIQUE,
	email VARCHAR(256) NOT NULL UNIQUE,
	password VARCHAR(256) NOT NULL,
	first_name VARCHAR(256) NULL,
	last_name VARCHAR(256) NULL,
	profile_pic VARCHAR(256) NULL,
	auth_token VARCHAR(40) UNIQUE,
	online BOOLEAN NOT NULL DEFAULT TRUE,
	FOREIGN KEY (id) REFERENCES clients (id)
);

DROP TABLE IF EXISTS teams CASCADE;
CREATE TABLE teams(
	id SERIAL,
	name VARCHAR(256) NOT NULL UNIQUE,
	location VARCHAR(256) NULL,
	description VARCHAR(256) NULL,
	welcome_message VARCHAR(256) NULL,
	PRIMARY KEY (id)
);

DROP TABLE IF EXISTS users_teams CASCADE;
CREATE TABLE users_teams(
	user_id INTEGER NOT NULL,
	team_id INTEGER NOT NULL,
	role TITLE NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users (id),
	FOREIGN KEY (team_id) REFERENCES teams (id)
);

DROP TABLE IF EXISTS channels CASCADE;
CREATE TABLE channels(
	id INTEGER NOT NULL UNIQUE,
	visibility VISIBILITY NOT NULL,
	description VARCHAR(256) NULL,
	welcome_message VARCHAR(256) NULL,
	FOREIGN KEY (id) REFERENCES clients (id)
);

DROP TABLE IF EXISTS users_channels CASCADE;
CREATE TABLE users_channels(
	user_id INTEGER NOT NULL,
	channel_id INTEGER NOT NULL,
	role TITLE NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users (id),
	FOREIGN KEY (channel_id) REFERENCES channels (id)
);

DROP TABLE IF EXISTS messages CASCADE;
CREATE TABLE messages(
	id SERIAL,
	sender_id INTEGER NOT NULL,
	receiver_id INTEGER NOT NULL,
	content VARCHAR(256) NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (sender_id) REFERENCES users (id),
	FOREIGN KEY (receiver_id) REFERENCES clients (id)
);

DROP TABLE IF EXISTS chats_messages CASCADE;
CREATE TABLE chats_messages(
	user_id INTEGER NOT NULL,
	chat_id INTEGER NOT NULL,
	unseen INTEGER NOT NULL DEFAULT 0,
	FOREIGN KEY (user_id) REFERENCES users (id),
	FOREIGN KEY (chat_id) REFERENCES clients (id)
);
