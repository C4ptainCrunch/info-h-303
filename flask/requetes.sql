-- R1:
select * from users where id in (select user_id from comment where etablissement_id in (SELECT etablissement_id FROM comment WHERE user_id=(SELECT id FROM users WHERE username='Brenda') and score > 3) and score > 3 GROUP BY user_id HAVING COUNT(*) >= 3);

-- R2:
select etablissement.* from comment join etablissement on comment.etablissement_id=etablissement.id and comment.score > 3 where comment.user_id in (select u.id from etablissement join comment on etablissement.id = comment.etablissement_id join users on comment.user_id = users.id join comment as c on etablissement.id = c.etablissement_id join users as u on c.user_id = u.id where users.username = 'Brenda' and comment.score >= 4 and u.username != 'Brenda' group by u.id having bool_and (c.score >= 4)) group by etablissement.id;

-- R3
select etablissement.* from etablissement left join comment on etablissement.id = comment.etablissement_id GROUP BY etablissement.id HAVING COUNT(*) <= 1;

-- R4:
select users.* from users where users.id in (select etablissement.user_id from etablissement left join comment on etablissement.id = comment.etablissement_id group by etablissement.id having bool_and(comment.user_id is NULL or comment.user_id != etablissement.user_id) order by etablissement.id);

-- R5:
select etablissement.* from etablissement join comment on etablissement.id = comment.etablissement_id GROUP BY etablissement.id HAVING COUNT(*) >=3 ORDER BY avg(score);

-- R6:
select label.name from label inner join (select etablissement_label.label_id, etablissement.id, avg(comment.score) as score from etablissement_label join etablissement on etablissement_label.etablissement_id = etablissement.id join comment on etablissement.id = comment.etablissement_id GROUP BY etablissement.id, etablissement_label.label_id) e on label.id = e.label_id GROUP BY label.id HAVING count(*) > 5 order by avg(e.score);
-- Inorrecte, à fixer car devrais renvoyer le même nombre de ligne que:
select label.name from label join etablissement_label on label.id = etablissement_label.label_id GROUP BY label.id HAVING count(*) > 5;
-- Should be working:
select label.* from label full join (select etablissement_label.label_id as id, avg(comment.score) as score from etablissement_label left join etablissement on etablissement_label.etablissement_id = etablissement.id full join comment on etablissement.id = comment.etablissement_id group by etablissement_label.label_id, etablissement.id) l on label.id = l.id group by label.id HAVING count(*) >= 5 order by avg(l.score);
-- group by etablissement_label.id instead
