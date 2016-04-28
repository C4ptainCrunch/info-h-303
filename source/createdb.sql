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
  --- address
    "address_street" VARCHAR(254),
    "address_number" INTEGER CHECK ("address_number" > 0),
    "address_zip" INTEGER CHECK ("address_zip" > 0),
    "address_city" VARCHAR(254),
  --- gps
    "latitude" NUMERIC(9, 6) CHECK("latitude" BETWEEN -180 AND 180),
    "longitude" NUMERIC(9, 6) CHECK("longitude" BETWEEN -180 AND 180),
  "created" DATE NOT NULL, -- creation > user.creation
  "user_id" INTEGER NOT NULL REFERENCES "user" ON DELETE RESTRICT,
  "type" etablissement_type NOT NULL,
  "picture" VARCHAR(100)
);

CREATE TABLE "hotel" (
  "etablissement_id" INTEGER PRIMARY KEY REFERENCES "etablissement" ON DELETE CASCADE,
  "stars" INTEGER NOT NULL CHECK ("stars" BETWEEN 0 AND 5),
  "rooms" INTEGER NOT NULL CHECK ("rooms" > 0),
  "price" INTEGER NOT NULL CHECK ("price" > 0)
);

CREATE TABLE "restaurant" (
  "etablissement_id" INTEGER PRIMARY KEY REFERENCES "etablissement" ON DELETE CASCADE,
  "price_range" INTEGER NOT NULL CHECK ("price_range" > 0),
  "max_seats" INTEGER NOT NULL CHECK ("max_seats" > 0),
  "takeaway" BOOLEAN NOT NULL,
  "delivery" BOOLEAN NOT NULL,
  "openings" BOOLEAN[14] NOT NULL
);

CREATE TABLE "bar" (
  "etablissement_id" INTEGER PRIMARY KEY REFERENCES "etablissement" ON DELETE CASCADE,
  "smoker" BOOLEAN NOT NULL,
  "food" BOOLEAN NOT NULL
);

CREATE TABLE "comment" (
  "id" SERIAL PRIMARY KEY,
  "user_id" INTEGER NOT NULL REFERENCES "user" ON DELETE CASCADE,
  "etablissement_id" INTEGER NOT NULL REFERENCES "etablissement" ON DELETE CASCADE,
  "date" DATE NOT NULL, -- check > etablissement.date AND > user.date
  "score" INTEGER NOT NULL CHECK ("score" BETWEEN 0 AND 5),
  "text" TEXT NOT NULL,
  UNIQUE ("date", "user_id")
);


CREATE TABLE "etablissement_label" (
  "id" SERIAL PRIMARY KEY,
  "etablissement_id" INTEGER NOT NULL REFERENCES "etablissement" ON DELETE CASCADE,
  "user_id" INTEGER NOT NULL REFERENCES "user" ON DELETE CASCADE,
  "label_id" INTEGER NOT NULL REFERENCES "label" ON DELETE CASCADE,
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
