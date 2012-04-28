cat ../schema.sql names/populate.sql teams/teams.sql teams/sports.sql workouts/workouts.sql > all.sql
mysql -e "source all.sql"
