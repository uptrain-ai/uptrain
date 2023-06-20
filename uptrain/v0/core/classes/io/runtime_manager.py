import os
from datetime import datetime, timedelta
import time
import pandas as pd
from uptrain.v0.core.lib.helper_funcs import dependency_required

try:
    from google.cloud import bigquery
except:
    bigquery = None

try:
    import psycopg2
except:
    psycopg2 = None


@dependency_required(bigquery, "'google-cloud-bigquery[pandas]'")
class BigQueryReader:
    def __init__(self, args) -> None:
        self.sql_query = args.sql_query
        self.client = bigquery.Client()
        self.sql_variables = args.sql_variables_dictn

    def run(self, time_diff):
        run_dict = {}
        for var, val in self.sql_variables.items():
            run_dict.update({
                var: str(val + timedelta(seconds=time_diff))
            })

        query = self.sql_query.format(**run_dict)
        print(f"Executing SQL query: {query} \n at UTC time: {str(datetime.utcnow())}")
        query_job = self.client.query(query)
        df = query_job.to_dataframe()
        print(f"Got {len(df)} rows")
        return df


@dependency_required(psycopg2, "psycopg2")
class PostgreSQLReader:
    def __init__(self, args) -> None:
        self.sql_query = args.sql_query
        self.conn = psycopg2.connect(
            database=args.database,
            user=os.environ['POSTGRES_USERNAME'],
            password=os.environ['POSTGRES_PASSWORD'])
        self.sql_variables = args.sql_variables_dictn

    def run(self, time_diff):
        run_dict = {}
        for var, val in self.sql_variables.items():
            run_dict.update({
                var: str(val + timedelta(seconds=time_diff))
            })

        query = self.sql_query.format(**run_dict)
        print(f"Executing SQL query: {query} \n at UTC time: {str(datetime.utcnow())}")
        df = pd.read_sql(query, self.conn)
        print(f"Got {len(df)} rows")
        return df


class RunTimeManager:
    def __init__(self, args, fw) -> None:
        self.framework = fw
        self.frequency_in_seconds = args.frequency_in_seconds
        self.num_backlog = args.num_backlog
        self.reader = self._resolve(args)
        self.time_diff = 0


    def run_endlessly(self):
        latest_run_time = datetime.utcnow() + timedelta(seconds=-self.frequency_in_seconds * self.num_backlog)
        while(1):
            if datetime.utcnow() > (latest_run_time + timedelta(seconds=self.frequency_in_seconds)):
                latest_run_time = latest_run_time + timedelta(seconds=self.frequency_in_seconds)
                data = self.reader.run(self.time_diff)
                if len(data) > 0:
                    self.framework.log(data)
                self.time_diff += self.frequency_in_seconds
            else:
                time.sleep(self.frequency_in_seconds * 0.1)


    def _resolve(self, args):
        if args.type == 'bigquery':
            return BigQueryReader(args)
        elif args.type == 'postgresql':
            return PostgreSQLReader(args)
        else:
            raise Exception(f"{args.type} is not supported!")