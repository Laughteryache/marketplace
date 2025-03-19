CREATE TABLE IF NOT EXISTS "users" (
	"id" bigserial NOT NULL UNIQUE,
	"login" varchar(25) NOT NULL UNIQUE,
	"email" varchar(50) NOT NULL UNIQUE,
	"hashed_password" varchar(500) NOT NULL,
	"role" varchar(10) NOT NULL,
	"is_deleted" boolean NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "businesses" (
	"id" bigserial NOT NULL UNIQUE,
	"login" varchar(25) NOT NULL UNIQUE,
	"hashed_password" varchar(500) NOT NULL,
	"email" varchar(50) NOT NULL UNIQUE,
	"is_deleted" boolean NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "reviews" (
	"id" bigserial NOT NULL UNIQUE,
	"creator_id" bigint NOT NULL,
	"product_id" bigint NOT NULL,
	"rate" smallint NOT NULL,
	"is_deleted" boolean NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "products" (
	"id" bigserial NOT NULL UNIQUE,
	"price" bigint NOT NULL,
	"name" varchar(50) NOT NULL,
	"creator_id" bigint NOT NULL,
	"category_id" smallint NOT NULL,
	"is_deleted" boolean NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "categories" (
	"id" serial NOT NULL UNIQUE,
	"name" varchar(50) NOT NULL UNIQUE,
	"description" varchar(500) NOT NULL,
	"is_deleted" boolean NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "orders" (
	"id" bigserial NOT NULL UNIQUE,
	"creator_id" bigint NOT NULL,
	"business_id" bigint NOT NULL,
	"promocode_id" bigint,
	"is_canceled" boolean NOT NULL,
	"is_deleted" boolean NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "promocodes" (
	"id" bigserial NOT NULL UNIQUE,
	"creator_id" bigint NOT NULL,
	"product_id" bigint NOT NULL,
	"name" varchar(255) NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "users_profile" (
	"user_id" bigint NOT NULL UNIQUE,
	"last_login" timestamp NOT NULL,
	"date_joined" timestamp NOT NULL,
	"location" varchar(90) NOT NULL,
	PRIMARY KEY ("user_id")
);

CREATE TABLE IF NOT EXISTS "users_cart" (
	"user_id" bigserial NOT NULL UNIQUE,
	"shopping_cart" integer[] NOT NULL,
	PRIMARY KEY ("user_id")
);

CREATE TABLE IF NOT EXISTS "users_balance" (
	"user_id" bigserial NOT NULL UNIQUE,
	"balance" bigint NOT NULL,
	PRIMARY KEY ("user_id")
);

CREATE TABLE IF NOT EXISTS "business_finances" (
	"business_id" bigserial NOT NULL UNIQUE,
	"balance" bigint,
	"revenue" bigint,
	"earnings" bigint,
	PRIMARY KEY ("business_id")
);

CREATE TABLE IF NOT EXISTS "business_profile" (
	"business_id" bigserial NOT NULL UNIQUE,
	"title" varchar(50),
	"description" varchar(500),
	"logo_id" varchar(255),
	"location" varchar(90),
	"date_joined" timestamp NOT NULL,
	PRIMARY KEY ("business_id")
);

CREATE TABLE IF NOT EXISTS "product_data" (
	"product_id" bigint NOT NULL UNIQUE,
	"description" varchar(500) NOT NULL,
	"logo_path" varchar(255),
	"sex" varchar(15) NOT NULL,
	"adult_only" boolean NOT NULL,
	PRIMARY KEY ("product_id")
);

CREATE TABLE IF NOT EXISTS "product_quanity" (
	"product_id" bigserial NOT NULL UNIQUE,
	"quanity" bigint,
	PRIMARY KEY ("product_id")
);

CREATE TABLE IF NOT EXISTS "promocode_discount" (
	"promocode_id" bigserial NOT NULL UNIQUE,
	"percent_off" smallint NOT NULL,
	"discount" smallint NOT NULL,
	PRIMARY KEY ("promocode_id")
);

CREATE TABLE IF NOT EXISTS "promo_quanity" (
	"promocode_id" bigserial NOT NULL UNIQUE,
	"quanity" bigint NOT NULL,
	PRIMARY KEY ("promocode_id")
);

CREATE TABLE IF NOT EXISTS "promocode_date" (
	"promocode_id" bigserial NOT NULL UNIQUE,
	"start_date" timestamp NOT NULL,
	"end_date" timestamp,
	PRIMARY KEY ("promocode_id")
);

CREATE TABLE IF NOT EXISTS "product_date" (
	"product_id" bigserial NOT NULL UNIQUE,
	"start_date" timestamp NOT NULL,
	"end_date" timestamp,
	PRIMARY KEY ("product_id")
);

CREATE TABLE IF NOT EXISTS "reviews_data" (
	"id" bigserial NOT NULL UNIQUE,
	"title" varchar(50) NOT NULL,
	"description" varchar(500) NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "order_date" (
	"order_id" bigserial NOT NULL UNIQUE,
	"start_date" timestamp NOT NULL,
	"end_date" timestamp,
	PRIMARY KEY ("order_id")
);

CREATE TABLE IF NOT EXISTS "order_price" (
	"order_id" bigserial NOT NULL UNIQUE,
	"price" bigint NOT NULL,
	"discounted_price" bigint NOT NULL,
	PRIMARY KEY ("order_id")
);

CREATE TABLE IF NOT EXISTS "order_cart" (
	"order_id" bigserial NOT NULL UNIQUE,
	"shopping_cart" integer[] NOT NULL,
	PRIMARY KEY ("order_id")
);



ALTER TABLE "reviews" ADD CONSTRAINT "reviews_fk1" FOREIGN KEY ("creator_id") REFERENCES "users"("id");
ALTER TABLE "reviews" ADD CONSTRAINT "reviews_fk2" FOREIGN KEY ("product_id") REFERENCES "products"("id");
ALTER TABLE "products" ADD CONSTRAINT "products_fk3" FOREIGN KEY ("creator_id") REFERENCES "businesses"("id");
ALTER TABLE "products" ADD CONSTRAINT "products_fk4" FOREIGN KEY ("category_id") REFERENCES "categories"("id");
ALTER TABLE "orders" ADD CONSTRAINT "orders_fk1" FOREIGN KEY ("creator_id") REFERENCES "users"("id");
ALTER TABLE "orders" ADD CONSTRAINT "orders_fk2" FOREIGN KEY ("business_id") REFERENCES "businesses"("id");
ALTER TABLE "orders" ADD CONSTRAINT "orders_fk3" FOREIGN KEY ("promocode_id") REFERENCES "promocodes"("id");
ALTER TABLE "promocodes" ADD CONSTRAINT "promocodes_fk1" FOREIGN KEY ("creator_id") REFERENCES "businesses"("id");
ALTER TABLE "promocodes" ADD CONSTRAINT "promocodes_fk2" FOREIGN KEY ("product_id") REFERENCES "products"("id");
ALTER TABLE "users_profile" ADD CONSTRAINT "users_profile_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "users_cart" ADD CONSTRAINT "users_cart_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "users_balance" ADD CONSTRAINT "users_balance_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "business_finances" ADD CONSTRAINT "business_finances_fk0" FOREIGN KEY ("business_id") REFERENCES "businesses"("id");
ALTER TABLE "business_profile" ADD CONSTRAINT "business_profile_fk0" FOREIGN KEY ("business_id") REFERENCES "businesses"("id");
ALTER TABLE "product_data" ADD CONSTRAINT "product_data_fk0" FOREIGN KEY ("product_id") REFERENCES "products"("id");
ALTER TABLE "product_quanity" ADD CONSTRAINT "product_quanity_fk0" FOREIGN KEY ("product_id") REFERENCES "products"("id");
ALTER TABLE "promocode_discount" ADD CONSTRAINT "promocode_discount_fk0" FOREIGN KEY ("promocode_id") REFERENCES "promocodes"("id");
ALTER TABLE "promo_quanity" ADD CONSTRAINT "promo_quanity_fk0" FOREIGN KEY ("promocode_id") REFERENCES "promocodes"("id");
ALTER TABLE "promocode_date" ADD CONSTRAINT "promocode_date_fk0" FOREIGN KEY ("promocode_id") REFERENCES "promocodes"("id");
ALTER TABLE "product_date" ADD CONSTRAINT "product_date_fk0" FOREIGN KEY ("product_id") REFERENCES "products"("id");
ALTER TABLE "reviews_data" ADD CONSTRAINT "reviews_data_fk0" FOREIGN KEY ("id") REFERENCES "reviews"("id");
ALTER TABLE "order_date" ADD CONSTRAINT "order_date_fk0" FOREIGN KEY ("order_id") REFERENCES "orders"("id");
ALTER TABLE "order_price" ADD CONSTRAINT "order_price_fk0" FOREIGN KEY ("order_id") REFERENCES "orders"("id");
ALTER TABLE "order_cart" ADD CONSTRAINT "order_cart_fk0" FOREIGN KEY ("order_id") REFERENCES "orders"("id");

INSERT INTO categories (id, name, description, is_deleted)
VALUES (1, 'all', 'All goods!', False)