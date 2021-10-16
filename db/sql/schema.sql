CREATE TABLE "User" (
        username           VARCHAR NOT NULL,
        email              VARCHAR NOT NULL,
        password           VARCHAR NOT NULL,
        name               VARCHAR NOT NULL,
        surname            VARCHAR NOT NULL,
        birthdate          DATE    NOT NULL,
        "registrationDate" DATE    NOT NULL,
        "isOperator"       BOOLEAN NOT NULL,
        PRIMARY KEY (username),
        UNIQUE (email)
);

CREATE TABLE "Genre" (
        name VARCHAR NOT NULL,
        PRIMARY KEY (name)
);

CREATE TABLE "Nation" (
        name VARCHAR NOT NULL,
        PRIMARY KEY (name)
);

CREATE TABLE "CastMember" (
        id      SERIAL  NOT NULL,
        name    VARCHAR NOT NULL,
        surname VARCHAR NOT NULL,
        PRIMARY KEY (id)
);

CREATE TABLE "PaymentCircuit" (
        name VARCHAR NOT NULL,
        PRIMARY KEY (name)
);

CREATE TABLE "Room" (
        name            VARCHAR NOT NULL,
        "numberOfRows"    INTEGER NOT NULL
                                  CONSTRAINT positive_number_of_rows
                                  CHECK ("numberOfRows" > 0),
        "numberOfColumns" INTEGER NOT NULL
                                  CONSTRAINT positive_number_of_cols
                                  CHECK ("numberOfColumns" > 0),
        "screenSize"      INTEGER NOT NULL
                                  CONSTRAINT positive_screen_size
                                  CHECK ("screenSize" > 0),
        PRIMARY KEY (name)
);

CREATE TABLE "Movie" (
        id            SERIAL  NOT NULL,
        title         VARCHAR NOT NULL,
        director      INTEGER NOT NULL,
        plot          TEXT    NOT NULL,
        duration      INTEGER NOT NULL
                              CONSTRAINT positive_duration
                              CHECK (duration > 0),
        genre         VARCHAR NOT NULL,
        nation        VARCHAR NOT NULL,
        "releaseDate" DATE    NOT NULL,
        poster        VARCHAR NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(director) REFERENCES "CastMember" (id)
                                ON UPDATE CASCADE
                                ON DELETE RESTRICT,
        FOREIGN KEY(genre)    REFERENCES "Genre" (name)
                                ON UPDATE CASCADE
                                ON DELETE RESTRICT,
        FOREIGN KEY(nation)   REFERENCES "Nation" (name)
                                ON UPDATE CASCADE
                                ON DELETE RESTRICT,
        UNIQUE (poster)
);

CREATE TABLE "PaymentMethod" (
        id               SERIAL  NOT NULL,
        "ownerName"      VARCHAR NOT NULL,
        "user"           VARCHAR NOT NULL,
        "cardNumber"     VARCHAR NOT NULL
                                 CONSTRAINT card_number_length
                                 CHECK (char_length("cardNumber") = 16),
        "expirationDate" DATE    NOT NULL,
        "paymentCircuit" VARCHAR NOT NULL,
        "isActive"       BOOLEAN NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY("user")           REFERENCES "User" (username)
                                        ON UPDATE CASCADE
                                        ON DELETE RESTRICT,
        FOREIGN KEY("paymentCircuit") REFERENCES "PaymentCircuit" (name)
                                        ON UPDATE CASCADE
                                        ON DELETE RESTRICT
);

CREATE TABLE "ActorMovie" (
        movie INTEGER NOT NULL,
        actor INTEGER NOT NULL,
        PRIMARY KEY (movie, actor),
        FOREIGN KEY(movie) REFERENCES "Movie" (id)
                             ON UPDATE CASCADE
                             ON DELETE CASCADE,
        FOREIGN KEY(actor) REFERENCES "CastMember" (id)
                             ON UPDATE CASCADE
                             ON DELETE RESTRICT
);

CREATE TABLE "Projection" (
        id       SERIAL                      NOT NULL,
        movie    INTEGER                     NOT NULL,
        room     VARCHAR                     NOT NULL,
        datetime TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        price    FLOAT                       NOT NULL
                                             CONSTRAINT positive_price
                                             CHECK (price > 0),
        PRIMARY KEY (id),
        FOREIGN KEY(movie) REFERENCES "Movie" (id)
                             ON UPDATE CASCADE
                             ON DELETE RESTRICT,
        FOREIGN KEY(room)  REFERENCES "Room" (name)
                             ON UPDATE CASCADE
                             ON DELETE RESTRICT,
        UNIQUE (datetime, room)
);

CREATE TABLE "Purchase" (
        id                 SERIAL                      NOT NULL,
        projection         INTEGER                     NOT NULL,
        total              FLOAT                       NOT NULL,
        "purchaseDatetime" TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        "paymentMethod"    INTEGER                     NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(projection)      REFERENCES "Projection" (id)
                                       ON UPDATE CASCADE
                                       ON DELETE RESTRICT,
        FOREIGN KEY("paymentMethod") REFERENCES "PaymentMethod" (id)
                                       ON UPDATE CASCADE
                                       ON DELETE RESTRICT
);

CREATE TABLE "Ticket" (
        id       SERIAL  NOT NULL,
        row      INTEGER NOT NULL
                         CONSTRAINT positive_row
                         CHECK (row > 0),
        "column" INTEGER NOT NULL
                         CONSTRAINT positive_column
                         CHECK ("column" > 0),
        purchase INTEGER NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(purchase) REFERENCES "Purchase" (id)
                                ON UPDATE CASCADE
                                ON DELETE RESTRICT
);
