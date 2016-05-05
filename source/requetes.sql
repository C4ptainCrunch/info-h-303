-- R1:
select * from "user" where id in (select user_id from comment where etablissement_id in (SELECT etablissement_id FROM comment WHERE user_id=(SELECT id FROM "user" WHERE username='Brenda') and score > 3) and score > 3 GROUP BY user_id HAVING COUNT(*) >= 3);

-- R3
select * from etablissement where id in (select etablissement_id from comment GROUP BY etablissement_id HAVING COUNT(*) <= 1);

-- R5:
select etablissement.* from etablissement join comment on etablissement.id = comment.etablissement_id GROUP BY etablissement.id HAVING COUNT(*) >=3 ORDER BY avg(score);
