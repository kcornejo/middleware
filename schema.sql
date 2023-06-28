DROP TABLE IF EXISTS contact;
DROP TABLE IF EXISTS message;

CREATE TABLE contact(
   id INT GENERATED ALWAYS AS IDENTITY,
   identifier VARCHAR(255) NOT NULL,
   blocked boolean NOT NULL,
   id_api VARCHAR(255) NOT NULL,
   PRIMARY KEY(id)
);

CREATE TABLE message(
   id INT GENERATED ALWAYS AS IDENTITY,
   contact_id INT,
   "content" VARCHAR(255) NOT NULL,
   "type" VARCHAR(10),
   datetime timestamp not null,
   sended boolean not null,
   PRIMARY KEY(id),
   CONSTRAINT fk_customer
      FOREIGN KEY(contact_id) 
	  REFERENCES contact(id)
);