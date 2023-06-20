# pip install psycopg2

import uptrain.v0 as uptrain
import datetime
import os


os.environ['POSTGRES_USERNAME'] = '...'
os.environ['POSTGRES_PASSWORD'] = '...'

# Make sure you have the following databases created
query_db = '...' # "test"
logs_db = '...' # "uptrain_logs"


do_setup = True
if do_setup:
    import psycopg2
    conn = None    
    try:
        conn = psycopg2.connect(
            database=query_db,
            user=os.environ['POSTGRES_USERNAME'],
            password=os.environ['POSTGRES_PASSWORD'])
        cur = conn.cursor()
        cur.execute("CREATE TABLE input (input_id int PRIMARY KEY, name VARCHAR (50))")
        cur.execute("ALTER TABLE input ADD COLUMN created_at TIMESTAMP DEFAULT NOW()")
        cur.execute("INSERT INTO input (input_id, name) VALUES (1, 'John')")
        cur.execute("INSERT INTO input (input_id, name) VALUES (2, 'Alice')")
        cur.execute("INSERT INTO input (input_id, name) VALUES (3, 'Mary')")
        conn.commit()
        # cur.execute('SELECT * FROM input')    
        # rows = cur.fetchall()
        # for row in rows:
        #     print(row)
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

# Base SQL query with time related filters
sql_query_base = """
        select name from input
        where created_at between '{t_start}' and '{t_end}'
        """

# Add your checks here
check1 = {
    "type": uptrain.Monitor.DATA_INTEGRITY,
    "measurable_args": {
        "type": uptrain.MeasurableType.INPUT_FEATURE,
        "feature_name": "name"
    },
    "integrity_type": "non_null"
}

cfg = {
    "checks": [check1],
    "reader_args": {
        # Continuous mode -> UpTrain will endlessly query the table for new data at specific frequency. Only continuous mode is supported
        'mode': 'continuous',

        # Time difference (in seconds) between two consecutive queries. For ex: UpTrain will wait for 600 secs before querying the table again for new data
        'frequency_in_seconds': 600,

        # Type of RDS - Only postgresql and bigquery is supported currently
        'type': 'postgresql',

        # Base SQL query, Final query will constructed from Base Query + Time dependent parameters
        'sql_query': sql_query_base,

        # Initial value of time-dependent parameters for the 1st run
        'sql_variables_dictn': {
            't_start': datetime.datetime.now() + datetime.timedelta(seconds=-600),
            't_end': datetime.datetime.now() + datetime.timedelta(seconds=0),
        },

        # Database to read from
        'database': query_db
    },

    "logging_args": {
        'postgres_logging': True,  # Turn postgres logging
        'database': logs_db  # Database to log to
    }
}

# Initialize the UpTrain framework
framework = uptrain.Framework(cfg_dict=cfg)

# Run the framework endlessly
framework.run_endlessly()