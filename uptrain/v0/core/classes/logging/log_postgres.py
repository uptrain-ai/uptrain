import os

try:
    import psycopg2
except:
    psycopg2 = None

from uptrain.v0.core.lib.helper_funcs import dependency_required


@dependency_required(psycopg2, "psycopg2")
class PostgresLogs:
    def __init__(self, db_name):
        self.conn = psycopg2.connect(
            database=db_name, user=os.environ['POSTGRES_USERNAME'], password=os.environ['POSTGRES_PASSWORD'])
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()
        self.tables_created = {}


    def add_scalars(self, dict, table_name, update_val=False):
        if self.tables_created.get(table_name, 0) == 0:
            schema = "(uptrain_log_id serial primary key, "
            for key, val in dict.items():
                if isinstance(val, int):
                    type = "INTEGER"
                elif isinstance(val, str):
                    type = "VARCHAR"
                elif isinstance(val, float):
                    type = "float"
                else:
                    raise Exception(f'{type(val)} not mapped to postgres')
                schema += key + " " + type + " NOT NULL, "
            schema = schema[0:-2] + ")"
            self.cursor.execute(f"""CREATE TABLE {table_name} {schema}""")
            print(f"Created table: {table_name}")
            self.tables_created[table_name] = 1

        if update_val:
            raise Exception("Not supported")
        else:
            keys = ', '.join(list(dict.keys()))
            vals = []
            for val in list(dict.values()):
                if isinstance(val, str):
                    vals.append(f"'{val}'")
                else:
                    vals.append(str(val))
            vals = ', '.join(vals)
            self.cursor.execute(f"""INSERT INTO {table_name} ({keys}) VALUES ({vals});""")
            # self.cursor.execute(f"SELECT * FROM {table_name}")
            # rows = self.cursor.fetchall()
            # for row in rows:
            #     print(row)
