DROP TABLE IF EXISTS contact;
DROP TABLE IF EXISTS message;

CREATE TABLE contact(
   id INT GENERATED ALWAYS AS IDENTITY,
   identifier VARCHAR(255) NOT NULL,
   "name" VARCHAR(255),
   blocked boolean NOT NULL,
   id_api VARCHAR(255) NOT NULL,
   PRIMARY KEY(id)
);

CREATE TABLE message(
   id INT GENERATED ALWAYS AS IDENTITY,
   contact_id INT,
   "content" VARCHAR NOT NULL,
   "type" VARCHAR(10),
   datetime timestamp not null,
   sended boolean not null,
   "error" VARCHAR,
   error_count INT,
   PRIMARY KEY(id),
   CONSTRAINT fk_customer
      FOREIGN KEY(contact_id) 
	  REFERENCES contact(id)
);
CREATE TABLE log(
   id INT GENERATED ALWAYS AS IDENTITY,
   "content" VARCHAR NOT NULL,
   datetime timestamp not null,
   PRIMARY KEY(id)
);

ALTER TABLE contact ADD "name" varchar(255) NULL;