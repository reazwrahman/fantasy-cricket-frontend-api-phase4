/* fantasy-cricket-db creation script */

CREATE DATABASE IF NOT EXISTS `fantasy-cricket-db`; 
USE `fantasy-cricket-db`;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS gameDetails;
CREATE TABLE gameDetails (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	game_title TEXT, 
	match_id BIGINT, 
	game_status TEXT, 
	squad_link TEXT, 
	scorecard_link TEXT, 
	points_per_run FLOAT, 
	points_per_wicket FLOAT, 
	game_start_time TEXT, 
	PRIMARY KEY (id)
);  

DROP TABLE IF EXISTS selectedSquad;
CREATE TABLE selectedSquad (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER, 
	match_id BIGINT, 
	selected_squad TEXT, 
	captain TEXT, 
	vice_captain TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

DROP TABLE IF EXISTS roles;
CREATE TABLE roles (
	id INTEGER NOT NULL, 
	name VARCHAR(64), 
	`default` BOOLEAN, 
	permissions INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (name), 
	CHECK (`default` IN (0, 1))
);  
DELETE FROM roles; 
INSERT INTO roles VALUES (1,"User",1,0); 
INSERT INTO roles VALUES (2,"Administrator",0,16);
 
DROP TABLE IF EXISTS users;
CREATE TABLE users (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	email VARCHAR(64), 
	username VARCHAR(64), 
	role_id INTEGER, 
	password_hash VARCHAR(128), 
	confirmed BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(role_id) REFERENCES roles (id), 
	CHECK (confirmed IN (0, 1))
); 

SET FOREIGN_KEY_CHECKS = 1;

