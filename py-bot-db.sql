CREATE TABLE phones (
  id SERIAL PRIMARY KEY,
  phone VARCHAR (255) UNIQUE NOT NULL
);

INSERT INTO phones (phone)
VALUES
	(88005553535),
	(89287775645),
	(96509087342)
;

CREATE TABLE emails (
  id SERIAL PRIMARY KEY,
  email VARCHAR (255) UNIQUE NOT NULL
);

INSERT INTO emails (email)
VALUES
	('test@mail.ru'),
	('asslan@yandex.ru'),
	('gus_777@gmail.com')
;