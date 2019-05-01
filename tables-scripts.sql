CREATE TYPE ROLE AS ENUM ('CREATOR', 'MODERATOR', 'MEMBER');
CREATE TYPE VISIBILITY AS ENUM ('PUBLIC', 'PRIVATE');

CREATE TABLE users(
	id SERIAL,
	username VARCHAR(256) NOT NULL UNIQUE,
	email VARCHAR(256) NOT NULL UNIQUE,
	password VARCHAR(256) NOT NULL,
	first_name VARCHAR(256) NULL,
	last_name VARCHAR(256) NULL,
	profile_pic VARCHAR(256) NULL,
	auth_token VARCHAR(40) UNIQUE,
	PRIMARY KEY (id)
);

CREATE TABLE teams(
	id SERIAL,
	name VARCHAR(256) NOT NULL UNIQUE,
	location VARCHAR(256) NOT NULL,
	description VARCHAR(256) NULL,
	welcome_message VARCHAR(256) NULL,
	PRIMARY KEY (id)
);

CREATE TABLE users_teams(
	user_id INTEGER NOT NULL,
	team_id INTEGER NOT NULL,
	role ROLE NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users (id),
	FOREIGN KEY (team_id) REFERENCES teams (id)
);

CREATE TABLE channels(
	id SERIAL,
	visibility VISIBILITY,
	description VARCHAR(256) NULL,
	welcome_message VARCHAR(256) NULL,
	PRIMARY KEY (id)
);

CREATE TABLE users_channels(
	user_id INTEGER NOT NULL,
	channel_id INTEGER NOT NULL,
	role ROLE NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users (id),
	FOREIGN KEY (channel_id) REFERENCES channels (id)
);