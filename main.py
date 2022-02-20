import requests
import pprint
import json
import sys
import sqlite3
from sqlite3 import Error
from time import time
import time as t


'''
Script has two modes: db init and runnig mode.\n
If argument -i is passed when running the script
db init mode is being executed.
'''

# ------------------- backend with sqlite3 -----------------


def create_connection(db_file):

    '''Creates a database connection to a SQLite database\n
    :param db_file: path to db file
    :return conn: connection object'''

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):

    ''' Creates a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:'''

    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_geoip(conn, entry):

    """Create new geoip entry."""

    sql = ''' INSERT INTO geoips(
        request_ip,
        status,
        delay,
        city,
        region,
        regionCode,
        regionName,
        areaCode,
        dmaCode,
        countryCode,
        countryName,
        inEU,
        euVATrate,
        continentCode,
        continentName,
        latitude,
        longitude,
        locationAccurancyRadius,
        timezone,
        currencyCode,
        currencySimbol,
        currencySimbol_UTF8,
        currencyConverter,
        timestamp)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, entry)
    conn.commit()

    return cur.lastrowid

# ------------------- ready to use sqlite3 functions -----------------


# initializing data base and creating table
def db_init():

    '''Initialise databse by passing -i arg when running script.\n
    DB will be saved in cwd. '''

    db_conn = create_connection(r'geoips.db')
    sql_create_geoips_table = '''CREATE TABLE IF NOT EXISTS geoips (
                                        id integer PRIMARY KEY,
                                        request_ip text,
                                        status integer NOT NULL,
                                        delay text,
                                        city text,
                                        region text,
                                        regionCode integer,
                                        regionName text,
                                        areaCode text,
                                        dmaCode text,
                                        countryCode text,
                                        countryName text,
                                        inEU integer,
                                        euVATrate text,
                                        continentCode text,
                                        continentName text,
                                        latitude real,
                                        longitude real,
                                        locationAccurancyRadius integer,
                                        timezone text,
                                        currencyCode text,
                                        currencySimbol text,
                                        currencySimbol_UTF8 text,
                                        currencyConverter real,
                                        timestamp real
                                    );'''
    if db_conn is not None:
        create_table(db_conn, sql_create_geoips_table)
    else:
        print("Error! cannot create the database connection.")


# adding new entry to the table based on API response
def add_new_entry(entry):

    '''Add new entry to db, user api.'''

    db_conn = create_connection(r'geoips.db')
    if db_conn is not None:
            create_geoip(db_conn, entry)
    else:
        print('Err')

if __name__ == '__main__':

    if len(sys.argv) > 1:
        if sys.argv.pop(1) == '-i':
            db_init()
    else:
        while True:
            r = requests.get(
                'http://www.geoplugin.net/json.gp?ip=<current_ip>'
            )
            response = r.json()
            timestamp_header = r.headers['date']
            timestamp_seconds = time()

            entry = (
                response['geoplugin_request'],
                response['geoplugin_status'],
                response['geoplugin_delay'],
                response['geoplugin_city'],
                response['geoplugin_region'],
                response['geoplugin_regionCode'],
                response['geoplugin_regionName'],
                response['geoplugin_areaCode'],
                response['geoplugin_dmaCode'],
                response['geoplugin_countryCode'],
                response['geoplugin_countryName'],
                response['geoplugin_inEU'],
                response['geoplugin_euVATrate'],
                response['geoplugin_continentCode'],
                response['geoplugin_continentName'],
                response['geoplugin_latitude'],
                response['geoplugin_longitude'],
                response['geoplugin_locationAccuracyRadius'],
                response['geoplugin_timezone'],
                response['geoplugin_currencyCode'],
                response['geoplugin_currencySymbol'],
                response['geoplugin_currencySymbol_UTF8'],
                response['geoplugin_currencyConverter'],
                timestamp_seconds
            )

            add_new_entry(entry)
            t.sleep(60)
