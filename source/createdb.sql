-- Types
------------------------------------

CREATE TYPE coordinate AS (
  "latitude" NUMERIC(9, 6),
  "longitude" NUMERIC(9, 6)
);

CREATE TYPE address AS (
  "street" VARCHAR(254),
  "number" INTEGER, -- CHECK ("number" > 0),
  "zip" INTEGER, -- CHECK ("zip" > 0),
  "city" VARCHAR(254)
);

CREATE TYPE etablissement_type AS ENUM ('restaurant', 'hotel', 'bar');

-- Tables
------------------------------------

CREATE TABLE "label" (
  "id" SERIAL PRIMARY KEY,
  "name" VARCHAR(254) NOT NULL UNIQUE
);

CREATE TABLE "user" (
  "id" SERIAL PRIMARY KEY,
  "username" VARCHAR(254) NOT NULL UNIQUE,
  "email" VARCHAR(254) NOT NULL UNIQUE,
  "password" VARCHAR(128) NOT NULL,
  "created" TIMESTAMP NOT NULL,
  "is_admin" BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE "etablissement" (
  "id" SERIAL PRIMARY KEY,
  "name" VARCHAR(254) NOT NULL,
  "phone" VARCHAR(20) NOT NULL,
  "url" TEXT,
  "address" address NOT NULL ,
  "gps" coordinate NOT NULL,
  "created" DATE NOT NULL, -- creation > user.creation
  "user_id" INTEGER NOT NULL REFERENCES "user",
  "type" etablissement_type NOT NULL
);

CREATE TABLE "hotel" (
  "etablissement_id" INTEGER PRIMARY KEY REFERENCES "etablissement",
  "stars" INTEGER NOT NULL CHECK ("stars" > 0 AND "stars" < 6),
  "rooms" INTEGER NOT NULL CHECK ("rooms" > 0),
  "price" INTEGER NOT NULL CHECK ("price" > 0)
);

CREATE TABLE "restaurant" (
  "etablissement_id" INTEGER PRIMARY KEY REFERENCES "etablissement",
  "price_range" INTEGER NOT NULL CHECK ("price_range" > 0),
  "max_seats" INTEGER NOT NULL CHECK ("max_seats" > 0),
  "takeaway" BOOLEAN NOT NULL,
  "delivery" BOOLEAN NOT NULL,
  "openings" BOOLEAN[14] NOT NULL
);

CREATE TABLE "bar" (
  "etablissement_id" INTEGER PRIMARY KEY REFERENCES "etablissement",
  "smoker" BOOLEAN NOT NULL,
  "food" BOOLEAN NOT NULL
);

CREATE TABLE "comment" (
  "id" SERIAL PRIMARY KEY,
  "user_id" INTEGER NOT NULL REFERENCES "user",
  "etablissement_id" INTEGER NOT NULL REFERENCES "etablissement",
  "date" DATE NOT NULL, -- check > etablissement.date AND > user.date
  "score" INTEGER NOT NULL CHECK ("score" > 0 AND "score" < 6),
  "text" TEXT NOT NULL,
  UNIQUE ("date", "user_id")
);


CREATE TABLE "etablissement_label" (
  "id" SERIAL PRIMARY KEY,
  "etablissement_id" INTEGER NOT NULL REFERENCES "etablissement",
  "user_id" INTEGER NOT NULL REFERENCES "user",
  "label_id" INTEGER NOT NULL REFERENCES "label",
  UNIQUE ("etablissement_id", "user_id", "label_id")
);


----------

-- CREATE ASSERTION partial CHECK (
--     NOT EXISTS (SELECT
--                   hotel.etablissement_id as hid,
--                   bar.etablissement_id as bid,
--                   restaurant.etablissement_id as rid,
--                 FROM hotel, bar, restaurant
--                 WHERE hid=bid OR bid=rid OR rid=hid))
