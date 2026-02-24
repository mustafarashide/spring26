"""
DO NOT MODIFY ANY VARIABLE NAMES. YOU MAY COMMENT YOUR CODE IF NEEDED.
"""

# You must fill in your Pennkey and your 8 digit Penn ID below:

pennkey = "murashid"
penn_id = "44270068"


## IMDB QUERIES (PART 1)

answer1 = """ 
SELECT DISTINCT C.person_id,P.name
FROM cast_in C,people P
WHERE C.person_id=P.id AND
      lower(name) LIKE '%john%' AND
      SUBSTRING(lower(name),2,1) NOT IN ('a','e','i','o','u') AND
      LENGTH(name) BETWEEN 10 AND 15
ORDER BY name;
"""

answer2 = """ 
SELECT DISTINCT C.person_id,P.name,P.death_year,M.id,M.title,M.release_year
FROM people P, cast_in C, movies M
WHERE C.person_id=P.id AND
      C.movie_id=M.id AND
      P.death_year<M.release_year
ORDER BY P.name,M.title DESC;
"""

answer3 = """
SELECT M.id,P.name,COUNT(*) as num_movies
FROM movies M, people P, crew_in C
WHERE C.person_id=P.id AND
      M.rating>8 AND
      M.release_year>2015 AND
      C.job LIKE 'director'
GROUP BY M.id,P.name
ORDER BY COUNT(*) DESC;
"""

answer4 = """
SELECT M.title,
       COUNT(CP.id) AS num_crew,
       STRING_AGG(CP.name, '; ' ORDER BY CP.name) AS CREW
FROM people P, movies M, crew_in C, known_for K, people CP
WHERE K.movie_id = M.id
  AND K.person_id = P.id
  AND C.movie_id = M.id
  AND C.person_id = CP.id
  AND P.name = 'Wes Anderson'
  AND M.num_ratings > 200000
GROUP BY M.id, M.title
ORDER BY M.title ASC, num_crew DESC;
"""

answer5 = """ 
SELECT M.id, M.title, ROUND( AVG( COALESCE( P.death_year - P.birth_year + 1, EXTRACT(YEAR FROM CURRENT_DATE)::INT - P.birth_year + 1 ) ) ) AS average_production_age
FROM movies M,
     people P,
     movie_genres MG,
     (
        SELECT movie_id, person_id FROM crew_in
        UNION
        SELECT movie_id, person_id FROM cast_in
     ) MC
WHERE M.id = MG.movie_id
  AND MG.genre = 'Drama'
  AND M.id = MC.movie_id
  AND P.id = MC.person_id
GROUP BY M.id, M.title
HAVING
    AVG(
        COALESCE(
            P.death_year - P.birth_year + 1,
            EXTRACT(YEAR FROM CURRENT_DATE)::INT - P.birth_year + 1
        )
    ) < 30
ORDER BY
    average_production_age,
    M.title;
    """

answer6 = """
WITH valid_movies AS (
  SELECT
    M.id,
    M.rating,
    M.num_ratings
  FROM movies M, movie_genres MG
  WHERE M.id = MG.movie_id
    AND M.rating IS NOT NULL
    AND M.num_ratings > 0
  GROUP BY M.id, M.rating, M.num_ratings
  HAVING COUNT(DISTINCT MG.genre) >= 3
),
valid_known_work AS (
  SELECT
    K.person_id,
    V.id AS movie_id,
    V.rating,
    V.num_ratings
  FROM known_for K, valid_movies V, crew_in CI
  WHERE K.movie_id = V.id
    AND CI.movie_id = V.id
    AND CI.person_id = K.person_id
    AND (CI.job = 'director' OR CI.job = 'producer')
)
SELECT
  P.id AS person_id,
  P.name,
  COUNT(DISTINCT VKW.movie_id) AS num_movies,
  ROUND(
    SUM(VKW.rating * VKW.num_ratings) / SUM(VKW.num_ratings),
    2
  ) AS average_rating
FROM valid_known_work VKW, people P
WHERE P.id = VKW.person_id
GROUP BY P.id, P.name
HAVING COUNT(DISTINCT VKW.movie_id) >= 3
ORDER BY average_rating DESC, P.name;
"""

answer7 = """ 
WITH credited AS (
    SELECT movie_id,person_id FROM cast_in
    UNION
    SELECT movie_id,person_id FROM crew_in
)
SELECT
    M.id AS movie_id,
    COUNT(DISTINCT C.person_id) AS prod_size
FROM movies M
JOIN credited C ON C.movie_id=M.id
WHERE M.num_ratings>0
GROUP BY M.id;
"""


## FLIGHTS DDL STATEMENTS (PART 2)

# Fill in DDL statements in the order of execution. A deduction might be applied for an incorrect order.
# Create query for ___
answer8a = """
CREATE TABLE airlines(
    id INT PRIMARY KEY,
    name VARCHAR(256),
    alias VARCHAR(256),
    iata CHAR(2),
    icao CHAR(3),
    callsign VARCHAR(255),
    country VARCHAR(255),
    active CHAR(1)
);
"""
# Create query for ___
answer8b = """
CREATE TABLE airports(
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    iata CHAR(3),
    icao CHAR(4),
    lat NUMERIC(8, 6),
    lon NUMERIC(9, 6),
    alt INT,
    timezone NUMERIC(3, 1),
    dst CHAR(1),
    tz VARCHAR(255)
);
"""
# Create query for ___
answer8c = """
CREATE TABLE routes(
    airline_iata CHAR(3),
    airline_id INT NOT NULL REFERENCES airlines(id),
    src_iata_icao CHAR(4),
    source_id INT NOT NULL REFERENCES airports(id),
    target_iata_icao CHAR(4),
    target_id INT NOT NULL REFERENCES airports(id),
    code_share CHAR(1) NOT NULL DEFAULT '',
    equipment CHAR(20),

    PRIMARY KEY (airline_id, source_id, target_id),

    CHECK (code_share IN ('Y', ''))
);
"""


## FLIGHTS QUERIES (PART 3)

answer9 = """
SELECT ALN.name AS airline, COUNT(*) as traffic_volume
FROM routes R
JOIN airports SRC ON SRC.id = R.source_id
JOIN airports TGT ON TGT.id = R.target_id
JOIN airlines ALN ON ALN.id = R.airline_id
WHERE SRC.city = 'New York' OR TGT.city = 'New York'
GROUP BY ALN.name
ORDER BY traffic_volume DESC, airline
LIMIT 5;
"""

answer10 = """
SELECT CAND.city, COUNT(*) AS num_cities
FROM (
  SELECT DISTINCT SRC.city, TGT.city AS other_city
  FROM airports SRC
  JOIN airports TGT
    ON SRC.country = 'Spain'
   AND TGT.country = 'Spain'
) AS CAND
JOIN (
  SELECT city
  FROM airports
  WHERE country = 'Spain'
  GROUP BY city
  HAVING COUNT(*) > 1
) AS ELIG
  ON ELIG.city = CAND.other_city
WHERE NOT EXISTS (
  SELECT 1
  FROM routes R
  JOIN airports S ON S.id = R.source_id
  JOIN airports T ON T.id = R.target_id
  WHERE S.country = 'Spain' AND T.country = 'Spain'
    AND (
      (S.city = CAND.city AND T.city = CAND.other_city)
      OR
      (S.city = CAND.other_city AND T.city = CAND.city)
    )
)
GROUP BY CAND.city
ORDER BY num_cities DESC, city
"""

answer11 = """
WITH SOURCES AS (
  SELECT id, iata
  FROM airports
  WHERE iata IS NOT NULL
),
ONE_HOP AS (
  SELECT R.source_id AS sid, DST.country AS country
  FROM routes R
  JOIN airports DST ON DST.id = R.target_id
),
two_hop AS (
  SELECT R1.source_id AS sid, DST2.country AS country
  FROM routes R1
  JOIN routes R2
    ON R1.target_id = R2.source_id
  JOIN airports DST2
    ON DST2.id = R2.target_id
),
upto2 AS (
  SELECT sid, country FROM ONE_HOP
  UNION
  SELECT sid, country FROM two_hop
),
one_hop_counts AS (
  SELECT sid, COUNT(DISTINCT country) AS countries_1hop
  FROM ONE_HOP
  GROUP BY sid
),
upto_2_counts AS (
  SELECT sid, COUNT(DISTINCT country) AS countries_upto2hop
  FROM upto2
  GROUP BY sid
)
SELECT
  SRC.iata,
  COALESCE(ohc.countries_1hop, 0) AS countries_1hop,
  COALESCE(u2.countries_upto2hop, 0) AS countries_upto2hop
FROM SOURCES SRC
LEFT JOIN one_hop_counts ohc ON ohc.sid = SRC.id
LEFT JOIN upto_2_counts u2 ON u2.sid = SRC.id
ORDER BY countries_upto2hop DESC, iata;
"""

answer12 = """
WITH direct AS (
    SELECT 1 AS num_flights, 'PHL;LIS' AS path
    FROM routes r
    JOIN airports src ON src.id = r.source_id
    JOIN airports dst ON dst.id = r.target_id
    WHERE src.iata = 'PHL' AND dst.iata = 'LIS'
),
through_cph AS (
    SELECT 1 AS num_flights, 'PHL;CPH;LIS' AS path
    FROM routes r1
    JOIN airports src ON src.id = r1.source_id
    JOIN airports cph ON cph.id = r1.target_id
    JOIN routes r2 ON cph.id = r2.source_id
    JOIN airports dst ON dst.id = r2.target_id
    WHERE src.iata = 'PHL' AND cph.iata = 'CPH' AND dst.iata = 'LIS'
),
two_hop AS (
    SELECT 2 AS num_flights, CONCAT('PHL;', x.iata, ';LIS') AS path
    FROM routes r1
    JOIN airports src ON src.id = r1.source_id
    JOIN airports x ON x.id = r1.target_id
    JOIN routes r2 ON x.id = r2.source_id
    JOIN airports dst ON dst.id = r2.target_id
    WHERE src.iata = 'PHL'
      AND dst.iata = 'LIS'
      AND x.iata NOT IN ('CPH', 'PHL', 'LIS')
),
cph_last AS (
    SELECT 2 AS num_flights, CONCAT('PHL;', x.iata, ';CPH;LIS') AS path
    FROM routes r1
    JOIN airports src ON src.id = r1.source_id
    JOIN airports x ON x.id = r1.target_id
    JOIN routes r2 ON x.id = r2.source_id
    JOIN airports cph ON cph.id = r2.target_id
    JOIN routes r3 ON cph.id = r3.source_id
    JOIN airports dst ON dst.id = r3.target_id
    WHERE src.iata = 'PHL'
      AND cph.iata = 'CPH'
      AND dst.iata = 'LIS'
      AND x.iata NOT IN ('PHL', 'LIS')
),
cph_first AS (
    SELECT 2 AS num_flights, CONCAT('PHL;CPH;', x.iata, ';LIS') AS path
    FROM routes r1
    JOIN airports src ON src.id = r1.source_id
    JOIN airports cph ON cph.id = r1.target_id
    JOIN routes r2 ON cph.id = r2.source_id
    JOIN airports x ON x.id = r2.target_id
    JOIN routes r3 ON x.id = r3.source_id
    JOIN airports dst ON dst.id = r3.target_id
    WHERE src.iata = 'PHL'
      AND cph.iata = 'CPH'
      AND dst.iata = 'LIS'
      AND x.iata NOT IN ('PHL', 'LIS')
)
SELECT DISTINCT num_flights, path
FROM (
    SELECT * FROM direct
    UNION ALL
    SELECT * FROM through_cph
    UNION ALL
    SELECT * FROM two_hop
    UNION ALL
    SELECT * FROM cph_last
    UNION ALL
    SELECT * FROM cph_first
) t
ORDER BY num_flights ASC, path ASC;
"""
