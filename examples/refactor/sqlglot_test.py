from sqlglot import parse_one, exp, parse

from uptrain.utilities.sql_utils import extract_tables_and_columns, extract_tables_and_columns_from_create

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

query = "SELECT x.a, y.c FROM x JOIN y ON x.a = y.b"
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
