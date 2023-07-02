from sqlglot import parse_one, exp, parse

from uptrain.utilities.sql_utils import extract_tables_and_columns, extract_tables_and_columns_from_create
# TODO: convert this into unit test
# print all column references (a and b)
for column in parse_one("SELECT *, b + 1 AS c FROM d").find_all(exp.Column):
    print(column.alias_or_name)

# find all projections in select statements (a and c)
for select in parse_one("SELECT a, b + 1 AS c FROM d").find_all(exp.Select):
    for projection in select.expressions:
        print(projection.alias_or_name)

# find all tables (x, y, z)
for table in parse_one("SELECT * FROM x JOIN y JOIN z").find_all(exp.Table):
    print(table)
    print(table.name)

for table in parse_one("SELECT x.a, y.c FROM x JOIN y ON x.a = y.b").find_all(exp.Table):
    print(table.name)

for table in parse_one("SELECT x.a, y.c FROM x JOIN y ON x.a = y.b").find_all(exp.Column):
    print(table.name)

query = "SELECT name as n FROM stadium EXCEPT SELECT T2.name FROM concert AS T1 JOIN stadium AS T2 ON T1.stadium_id  =  T2.stadium_id WHERE T1.year  =  2014"
parsed = parse(query)
print(type(parsed[0]))
print(parsed[0])
tables_and_columns = extract_tables_and_columns(parsed[0])
print(tables_and_columns)

query = """SELECT s.Name, s.Song_release_year
FROM singer s
WHERE s.Age = (SELECT MIN(Age) FROM singer)
LIMIT 1;"""
parsed = parse(query)
print(type(parsed[0]))
print(parsed[0])
tables_and_columns = extract_tables_and_columns(parsed[0])
print(tables_and_columns)

query = """
CREATE TABLE "stadium" (
"Stadium_ID" int,
"Location" text,
"Name" text,
"Capacity" int,
"Highest" int,
"Lowest" int,
"Average" int,
PRIMARY KEY ("Stadium_ID")
)
"""
parsed = parse(query)
print(type(parsed[0]))
print(parsed[0])
tables_and_columns = extract_tables_and_columns_from_create(parsed[0])
print(tables_and_columns)

query = """
create table Student (
       StuID            INTEGER PRIMARY KEY,
       LName            VARCHAR(12),
       Fname            VARCHAR(12),
       Age              INTEGER,
       Sex              VARCHAR(1),
       Major            INTEGER,
       Advisor          INTEGER,
       city_code        VARCHAR(3)
);
"""
parsed = parse(query)
print(type(parsed[0]))
print(parsed[0])
tables_and_columns = extract_tables_and_columns_from_create(parsed[0])
print(tables_and_columns)
