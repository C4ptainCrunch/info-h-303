-- R1:
select * from "user" where id in (select user_id from comment where etablissement_id in (SELECT etablissement_id FROM comment WHERE user_id=(SELECT id FROM "user" WHERE username='Brenda') and score > 3) and score > 3 GROUP BY user_id HAVING COUNT(*) >= 3);

-- R3
select * from etablissement where id in (select etablissement_id from comment GROUP BY etablissement_id HAVING COUNT(*) <= 1);

-- R5:
select etablissement.* from etablissement join comment on etablissement.id = comment.etablissement_id GROUP BY etablissement.id HAVING COUNT(*) >=3 ORDER BY avg(score);

-- R6:
select label.name from label inner join (select etablissement_label.label_id, etablissement.id, avg(comment.score) as score from etablissement_label join etablissement on etablissement_label.etablissement_id = etablissement.id join comment on etablissement.id = comment.etablissement_id GROUP BY etablissement.id, etablissement_label.label_id) e on label.id = e.label_id GROUP BY label.id HAVING count(*) > 5 order by avg(e.score);
-- Inorrecte, à fixer car devrais renvoyer le même nombre de ligne que:
select label.name from label join etablissement_label on label.id = etablissement_label.label_id GROUP BY label.id HAVING count(*) > 5;
-- Should be working:
select label.* from label full join (select etablissement_label.label_id as id, avg(comment.score) as score from etablissement_label left join etablissement on etablissement_label.etablissement_id = etablissement.id full join comment on etablissement.id = comment.etablissement_id group by etablissement_label.label_id, etablissement.id, etablissement_label.user_id) l on label.id = l.id group by label.id HAVING count(*) >= 5 order by avg(l.score);
