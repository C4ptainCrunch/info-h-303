-- R1:
select * from "user" where id in (select user_id from comment where etablissement_id in (SELECT etablissement_id FROM comment WHERE user_id=(SELECT id FROM "user" WHERE username='Brenda') and score > 3) and score > 3 GROUP BY user_id HAVING COUNT(*) >= 3);

-- R2:
select u.* from etablissement join comment on etablissement.id = comment.etablissement_id join "user" on comment.user_id = "user".id join comment as c on etablissement.id = c.etablissement_id join "user" as u on c.user_id = u.id where "user".username = 'Brenda' and comment.score >= 4 and u.username != 'Brenda' group by u.id having bool_and (c.score >= 4);

-- R3
select * from etablissement where id in (select etablissement_id from comment GROUP BY etablissement_id HAVING COUNT(*) <= 1);

-- R4:
select "user".* from "user" where "user".id in (select etablissement.user_id from etablissement left join comment on etablissement.id = comment.etablissement_id group by etablissement.id having bool_and(comment.user_id is NULL or comment.user_id != etablissement.user_id) order by etablissement.id);

-- R5:
select etablissement.* from etablissement join comment on etablissement.id = comment.etablissement_id GROUP BY etablissement.id HAVING COUNT(*) >=3 ORDER BY avg(score);

-- R6:
select label.name from label inner join (select etablissement_label.label_id, etablissement.id, avg(comment.score) as score from etablissement_label join etablissement on etablissement_label.etablissement_id = etablissement.id join comment on etablissement.id = comment.etablissement_id GROUP BY etablissement.id, etablissement_label.label_id) e on label.id = e.label_id GROUP BY label.id HAVING count(*) > 5 order by avg(e.score);
-- Inorrecte, à fixer car devrais renvoyer le même nombre de ligne que:
select label.name from label join etablissement_label on label.id = etablissement_label.label_id GROUP BY label.id HAVING count(*) > 5;
-- Should be working:
select label.* from label full join (select etablissement_label.label_id as id, avg(comment.score) as score from etablissement_label left join etablissement on etablissement_label.etablissement_id = etablissement.id full join comment on etablissement.id = comment.etablissement_id group by etablissement_label.label_id, etablissement.id, etablissement_label.user_id) l on label.id = l.id group by label.id HAVING count(*) >= 5 order by avg(l.score);
-- group by etablissement_label.id instead
