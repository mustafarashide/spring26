# Question 7
answer_7 = """
WITH TargetMovie AS (
    SELECT s.embedding
    FROM synopses s
    JOIN movies m ON s.movie_id = m.id
    WHERE m.title = 'The Lord of the Rings: The Fellowship of the Ring'
    LIMIT 1
),
SimilarNeighbors AS (
    SELECT s.movie_id
    FROM synopses s, TargetMovie t
    WHERE s.movie_id <> (SELECT id FROM movies WHERE title = 'The Lord of the Rings: The Fellowship of the Ring')
    ORDER BY s.embedding <=> t.embedding ASC
    LIMIT 50
)
SELECT mg.genre AS genre_name, COUNT(*) AS genre_count
FROM SimilarNeighbors sn
JOIN movie_genres mg ON sn.movie_id = mg.movie_id
GROUP BY mg.genre
ORDER BY genre_count DESC, genre_name ASC
LIMIT 5;
"""

# Question 8
answer_8 = """
WITH KeanuMovies AS (
    SELECT m.id, m.title, s.embedding
    FROM movies m
    JOIN synopses s ON m.id = s.movie_id
    JOIN known_for kf ON m.id = kf.movie_id
    JOIN people p ON kf.person_id = p.id
    WHERE p.name = 'Keanu Reeves'
),
RomanceMovies AS (
    SELECT m.id, m.title, s.embedding
    FROM movies m
    JOIN synopses s ON m.id = s.movie_id
    JOIN movie_genres mg ON m.id = mg.movie_id
    WHERE mg.genre = 'Romance'
)
SELECT
    km.title AS keanu_movie_title,
    rm.title AS romance_movie_title,
    ROUND((1 - (km.embedding <=> rm.embedding))::numeric, 2) AS cosine_similarity
FROM KeanuMovies km
CROSS JOIN RomanceMovies rm
WHERE km.id <> rm.id
ORDER BY cosine_similarity DESC
LIMIT 10;
"""
