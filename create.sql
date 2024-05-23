CREATE Database test_3;

CREATE TABLE Articles (ID serial NOT NULL PRIMARY KEY,
					Art_id_hubr integer NOT NULL UNIQUE,
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
						 hash text not Null,
						 FOREIGN KEY(art_id) REFERENCES articles(ID),
						 FOREIGN KEY(auth_id) REFERENCES authors(auth_id));

CREATE USER pli WITH password '12345' CONNECTION LIMIT 1;

GRANT SELECT, UPDATE, INSERT ON Authors TO pli;
GRANT SELECT, UPDATE, INSERT ON Articles TO pli;
GRANT SELECT, UPDATE, INSERT ON Auth_art_id TO pli;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO pli;                         

 GRANT SELECT ON Authors to server;                      
GRANT SELECT ON Articles to server;
GRANT SELECT ON Auth_art_id to server;    

                         