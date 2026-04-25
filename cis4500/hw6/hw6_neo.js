// Question 4
var answer_4 = `MATCH (f:Flight)
WHERE f.departure < 600 AND f.carrier CONTAINS 'Air'
RETURN f.code AS code, f.carrier AS carrier, f.departure AS departure, f.source_airport_code AS airport
ORDER BY f.departure ASC`

// Question 5
var answer_5 = `MATCH (london:City {name: 'London'})-[:HAS_FLIGHT]->(outbound:Flight)-[:FLYING_TO]->(dest:City)
MATCH (dest)-[:HAS_FLIGHT]->(return:Flight)-[:FLYING_TO]->(london)
WHERE return.departure - outbound.arrival >= 120
  AND return.departure - outbound.arrival <= 480
  AND outbound.departure < return.departure
WITH dest.name AS `destination city`, 
     outbound.code AS outbound_code, 
     return.code AS return_code, 
     (return.departure - outbound.arrival) AS waiting_time
RETURN `destination city`, outbound_code, return_code, waiting_time
ORDER BY waiting_time ASC`

// Question 6
var answer_6 = ``

// DO NOT MODIFY BELOW THIS LINE
module.exports = { answer_4, answer_5, answer_6 }
