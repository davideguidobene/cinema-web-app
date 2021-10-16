
-- QUERY_1

-- mostra i generi più comuni tra i film proiettati dal cinema in ordine non crescente (decrescente)
-- conta il numero di film per ogni genrere
SELECT "Movie".genre, count(*) AS genre_count
FROM "Movie"
GROUP BY "Movie".genre
ORDER BY genre_count DESC



-- QUERY_2

-- mostra i generi di film più popolari tra i clienti del cinema in ordine non crescente (decrescente)
-- conta numero di biglietti venduti per genere
SELECT "Movie".genre, count(*) AS genre_count
FROM "Movie", "Projection", "Purchase", "Ticket"
WHERE "Movie".id = "Projection".movie
  AND "Projection".id = "Purchase".projection
  AND "Purchase".id = "Ticket".purchase
GROUP BY "Movie".genre
ORDER BY genre_count DESC



-- QUERY_3

-- mostra i generi di film del cinema più redditizi in ordine non crescente (decrescente)
-- calcola entrate per ogni genere
SELECT "Movie".genre, sum("Purchase".total) AS genre_profit
FROM "Movie", "Purchase", "Projection"
WHERE "Movie".id = "Projection".movie AND "Projection".id = "Purchase".projection
GROUP BY "Movie".genre
ORDER BY genre_profit DESC


-- QUERY_4

-- mostra i generi di film più popolari tra i clienti del cinema in base all'età in ordine dagli utenti più giovani ai più vecchi
-- mostra per ogni genere, quali sono le fascie d'età che lo seguono di più
SELECT "Genre".name
FROM "Genre" ORDER BY "Genre".name

SELECT "Movie".genre,
        count(*) AS ticket_count
        CASE
          WHEN (
              EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) >= 0
              AND EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) <= 19
          ) THEN '0-19'

          WHEN (
            EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) >= 20
            AND EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) <= 29
          ) THEN '20-29'

          WHEN (EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) >= 30 AND EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) <= 39) THEN '30-39'
          WHEN (EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) >= 40 AND EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) <= 49) THEN '40-49'
          WHEN (EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) >= 50 AND EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) <= 59) THEN '50-59'
          WHEN (EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) >= 60 AND EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) <= 69) THEN '60-69'
          WHEN (EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) >= 70 AND EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) <= 79) THEN '70-79'
          WHEN (EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) >= 80 AND EXTRACT(year FROM CURRENT_DATE) - EXTRACT(year FROM "User".birthdate) <= 99) THEN '80-99'
          ELSE '100+'
        END AS age_group
FROM "Movie", "User", "Projection", "Purchase", "Ticket", "PaymentMethod"
WHERE "Movie".id = "Projection".movie
  AND "Projection".id = "Purchase".projection
  AND "Purchase".id = "Ticket".purchase
  AND "Purchase"."paymentMethod" = "PaymentMethod".id
  AND "PaymentMethod"."user" = "User".username
GROUP BY age_group, "Movie".genre
ORDER BY ticket_count DESC



-- QUERY_6

-- mostra i generi più comuni nel trend degli ultimi 9 mesi tra i film proiettati dal cinema in ordine non crescente (decrescente)
SELECT "Movie".genre, count(*) AS genre_count
FROM "Movie"
WHERE "Movie"."releaseDate" + INTERVAL'1 day'*9*30 >= CURRENT_DATE
GROUP BY "Movie".genre
ORDER BY genre_count DESC


-- QUERY_7

-- mostra i generi di film più popolari degli ultimi 9 mesi tra i clienti del cinema in ordine non crescente (decrescente)
SELECT "Movie".genre, count(*) AS genre_count
FROM "Movie", "Projection", "Purchase", "Ticket"
WHERE "Movie".id = "Projection".movie
  AND "Projection".id = "Purchase".projection
  AND "Purchase".id = "Ticket".purchase
  AND "Movie"."releaseDate" + INTERVAL'1 day'*9*30 >= CURRENT_DATE
GROUP BY "Movie".genre
ORDER BY genre_count DESC


-- QUERY_8

-- mostra i generi di film del cinema più redditizi negli ultimi 9 mesi in ordine non crescente (decrescente)
SELECT "Movie".genre, sum("Purchase".total) AS genre_profit
FROM "Movie", "Purchase", "Projection"
WHERE "Movie".id = "Projection".movie
  AND "Projection".id = "Purchase".projection
  AND "Movie"."releaseDate" + INTERVAL'1 day'*9*30 >= CURRENT_DATE
GROUP BY "Movie".genre
ORDER BY genre_profit DESC


-- QUERY_9

-- mostra gli attori più popolari tra i clienti del cinema in ordine non crescente (decrescente)
-- attori che hanno venduto più biglietti
SELECT "CastMember".name, "CastMember".surname, count(*) AS ticket_count
FROM "CastMember", "ActorMovie", "Movie", "Projection", "Purchase", "Ticket"
WHERE "CastMember".id = "ActorMovie".actor
  AND "ActorMovie".movie = "Movie".id
  AND "Movie".id = "Projection".movie
  AND "Projection".id = "Purchase".projection
  AND "Purchase".id = "Ticket".purchase
GROUP BY "CastMember".id
ORDER BY ticket_count DESC
LIMIT 25


-- QUERY_10

-- mostra i registi più popolari tra i clienti del cinema in ordine non crescente (decrescente)
-- registi che hanno venduto più biglietti
SELECT "CastMember".name, "CastMember".surname, count(*) AS ticket_count
FROM "CastMember", "Movie", "Projection", "Purchase", "Ticket"
WHERE "CastMember".id = "Movie".director
  AND "Movie".id = "Projection".movie
  AND "Projection".id = "Purchase".projection
  AND "Purchase".id = "Ticket".purchase
GROUP BY "CastMember".id
ORDER BY ticket_count DESC
LIMIT 25
