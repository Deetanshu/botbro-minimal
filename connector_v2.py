# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 11:13:57 2019

@author: Deeptanshu Paul

NOTES:
These are connectors to MySQL and PostgreSQL. Remember that the IP address from which access is trying to be made needs to be whitelisted in order for this to work.

V2 changes:
- Created BigQuery connector.
- Created a simple query execution framework.
- Updated the execution patterns for Postgres as well as mySQL.

To-do:
- More documentation regarding the functions
- Add more "native" functionality
- Create connectors to bigquery, datastore, etc. 
"""

#Imports
import pandas as pd
import pymysql
#import psycopg2
from sqlalchemy import create_engine
from threading import Thread


class postgres():
    """
    This class is used to connect to postgres. This can be directly created and then used with pandas.
    Alternatively, this class can be created as an object in sql_connector.

    connect(): The execution string is:
    "postgresql+psycopg2://user:password@host:port/dbname"
    to connect. This function creates that connection.

    """
    def __init__(self, user, password, host, port, dbname, isVerbose=0):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.dbname = dbname
        self.engine = None
        self.isVerbose = isVerbose

    def connect(self):
        if self.port == "":
            ex_str = str('postgresql+psycopg2://'+self.user+':'+self.password+'@'+self.host+'/'+self.dbname)
        else:
            ex_str = str('postgresql+psycopg2://'+self.user+':'+self.password+'@'+self.host+':'+self.port+'/'+self.dbname)
        if self.isVerbose == 1:
            print("[INFO] Connecting to PostgreSQL instance. ")
        self.engine = create_engine(ex_str)

        if self.isVerbose == 1:
            if self.engine == None:
                print("[INFO] Connection to PostgreSQL instance failed.")
            else:
                print("[INFO] Connection to PostgreSQL instance at "+self.host+":"+self.port+" is successful.")

class mysql():
    """
    This class connects to mysql. This can be directly created and called if needed, however it is recommended that an sql_connector object be made as there is functionality added to it.
    
    connect(): The execution string is:
    "mysql+pymysql://username:password@host:port/database"
    to connect. This function creates that connection
    """
    def __init__(self, username, password, host, port, database_name, isVerbose=0):
        self.username = username
        self.host = host
        self.port = port
        self.database_name = database_name
        self.engine = None
        self.isVerbose = isVerbose
        self.password = password

    def connect(self):
        ex_str = str('mysql+pymysql://'+self.username+':'+self.password+'@'+self.host)
        if self.port is not None:
            ex_str = str(ex_str+':'+str(self.port)+'/'+str(self.database_name))
        else:
            ex_str = ex_str+'/'+str(self.database_name)
        if self.isVerbose == 1:
            print("[INFO] Connecting to PostgreSQL instance. ")

        self.engine = create_engine(ex_str)
        if self.isVerbose == 1:
            if self.engine == None:
                print("[INFO] Connection to MySQL instance failed.")
            else:
                print("[INFO] Connection to MySQL instance at "+self.host+":"+self.port+" is successful.")

class sql_connector():
    """
    This class is a generic sql connector that encapsulates either a mysql or postgres connector and provides basic functionality.
    """
    def __init__(self, db_type, user, password, host, port, dbname, isVerbose = 0):
        self.c_type = db_type
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.dbname = dbname
        self.isVerbose = isVerbose
        self.engine = None
        self.db_obj = None
        self.welcome()
    
    def welcome(self):
        if self.c_type != "postgres" and self.c_type != 'mysql':
            print("[ERROR] Wrong type. Valid types are \"postgres\" or \"mysql\"")
            return False
        elif self.c_type == "postgres":
            self.db_obj = postgres(self.user, self.password, self.host, self.port, self.dbname, self.isVerbose)
        else:
            self.db_obj = mysql(self.user, self.password, self.host, self.port, self.dbname, self.isVerbose)
        self.db_obj.connect()
        self.engine = self.db_obj.engine
    
    def select_star(self, tablename):
        if self.engine == None:
            print("[ERROR] Connection not initialized. Please re-create this object.")
            return None
        ex_str = str('SELECT * FROM '+tablename+';')
        df = pd.read_sql_query(ex_str, self.engine)
        if self.isVerbose == 1:
            print("[INFO] Executed query "+ex_str)
        return df
    
    def execute(self, query):
        daemon = Thread(target=self.execute_query, daemon = True, name="sql_runner", args=(query,))
        daemon.start()

    def execute_query(self, query):
        if self.engine == None:
            self.welcome()
            return None
        if len(query) == 0:
            return None
        if query[-1] != ';':
            query = query + ';'
        try:
            df = pd.read_sql_query(query, self.engine)
            if self.isVerbose == 1:
                print("[INFO] Executed query "+query)
            return df
        except Exception as e:
            if str(e) == "This result object does not return rows. It has been closed automatically.":
                return None 
            else:
                print(e)
            return None
        
    
"""
class BigQuery():
    def __init__(self, project = None, credentials = None, client=None):
        self.project = project
        self.credentials = credentials
        self.client = bigquery.Client(project = self.project, credentials = self.credentials) if client is None else client
    
    def execute(self, query, isDataFrame = True):
        job = self.client.query(query)
        results = job.result()
        results = results.to_dataframe()
        if isDataFrame:
            return results
        else:
            return results.values.tolist()
        """