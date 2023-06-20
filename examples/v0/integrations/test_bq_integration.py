# pip install 'google-cloud-bigquery[pandas]'

import uptrain
import datetime
import os

# Add your BQ credentials file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '...'

# Base SQL query with time related filters
sql_query_base = """
        select COL_1, COL_2, ... from TABLE_NAME
        where COL_TIME between '{t_start}' and '{t_end}'
        """

# Add your checks here
check1 = {}
check2 = {}

cfg = {
    "checks": [check1, check2],
    "reader_args": {
        # Continuous mode -> UpTrain will endlessly query the table for new data at specific frequency. Only continuous mode is supported
        'mode': 'continuous',

        # Time difference (in seconds) between two consecutive queries. For ex: UpTrain will wait for 600 secs before querying the table again for new data
        'frequency_in_seconds': 600,

        # Type of RDS - Only Bigquery is supported currently
        'type': 'bigquery',

        # Base SQL query, Final query will constructed from Base Query + Time dependent parameters
        'sql_query': sql_query_base,

        # Initial value of time-dependent parameters for the 1st run
        'sql_variables_dictn': {
            't_start': datetime.datetime.utcnow() + datetime.timedelta(seconds=-600),
            't_end': datetime.datetime.utcnow() + datetime.timedelta(seconds=-600),
        }
    }
}

# Initialize the UpTrain framework
framework = uptrain.Framework(cfg_dict=cfg)

# Run the framework endlessly
framework.run_endlessly()