Video link:

Install instructions:
pip3 install -r requirements.txt

Database Setup:
#open psql 
psql -d postgres
#Create gym_db
CREATE DATABASE gym_db;
#quit psql for now
\q
#load DDL
psql -d gym_db -f sql/DDL.sql
#populate database
psql -d gym_db -f sql/DML.sql;
#make sure the database was populated successfully
psql -d postgres
\c gym_db
SELECT * FROM scheduled_class;