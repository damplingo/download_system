CREATE Database test;

CREATE TABLE Articles (art_id serial NOT NULL PRIMARY KEY,
					 Title text,
					 publication_date timestamp NOT NULL,
					 content text NOT NULL,
					 tags text[]);

CREATE TABLE Authors (Auth_id serial not null primary key,
					name text not null,
					registration_date date);

CREATE TABLE Auth_art_id (G_ID serial NOT NULL PRIMARY KEY,
						 art_id integer NOT NULL,
						 auth_id integer NOT NULL,
						 FOREIGN KEY(art_id) REFERENCES articles(art_id),
						 FOREIGN KEY(auth_id) REFERENCES authors(auth_id));

CREATE USER pi WITH password '12345' CONNECTION LIMIT 1;

GRANT SELECT, UPDATE, INSERT ON Authors TO pi;
GRANT SELECT, UPDATE, INSERT ON Articles TO pi;
GRANT SELECT, UPDATE, INSERT ON Auth_art_id TO pi;                         


                         