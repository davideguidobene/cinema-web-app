-- Crea ruoli e garantisce loro i privilegi necessari

-- client role

-- crea il ruolo client
CREATE ROLE client;

-- concede il permesso di usare sequenze (necessario per inserimento in tabelle con attributi con autoincremento)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO client;

-- concede permessi sulle tabelle
GRANT SELECT, INSERT, UPDATE(username, email, password, name, surname, birthdate) ON "User" TO client;
GRANT SELECT ON "Movie" TO client;
GRANT SELECT ON "Genre" TO client;
GRANT SELECT ON "Room" TO client;
GRANT SELECT ON "Projection" TO client;
GRANT SELECT, INSERT, UPDATE("isActive") ON "PaymentMethod" TO client;
GRANT SELECT ON "PaymentCircuit" TO client;
GRANT SELECT, INSERT ON "Purchase" TO client;
GRANT SELECT ON "ActorMovie" TO client;
GRANT SELECT ON "CastMember" TO client;
GRANT SELECT ON "Nation" TO client;
GRANT SELECT, INSERT ON "Ticket" TO client;

-- concede il ruolo client a webapp
GRANT client to webapp;

----------------------------------------------------------------------------------------------------

-- operator role

-- crea il ruolo operator
CREATE ROLE operator;

-- concede il permesso di usare sequenze (necessario per inserimento in tabelle con attributi con autoincremento)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO operator;

-- concede permessi sulle tabelle
GRANT SELECT, INSERT, UPDATE, DELETE ON "CastMember" TO operator;
GRANT SELECT, INSERT, UPDATE, DELETE ON "Room" TO operator;
GRANT SELECT, INSERT, UPDATE, DELETE ON "Movie" TO operator;
GRANT SELECT, INSERT, UPDATE, DELETE ON "Genre" TO operator;
GRANT SELECT, INSERT, UPDATE, DELETE ON "Nation" TO operator;
GRANT SELECT, UPDATE("isOperator", password) ON "User" TO operator;
-- GRANT **NOTHING** ON "PaymentMethod" TO operator;
GRANT SELECT, INSERT, UPDATE, DELETE ON "PaymentCircuit" TO operator;
GRANT SELECT, INSERT, UPDATE, DELETE ON "ActorMovie" TO operator;
GRANT SELECT, INSERT, UPDATE(price), DELETE ON "Projection" TO operator;
GRANT SELECT ON "Purchase" TO operator;
GRANT SELECT ON "Ticket" TO operator;

-- concede il ruolo client a webapp
GRANT operator to webapp;
