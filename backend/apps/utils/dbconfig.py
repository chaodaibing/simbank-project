import configparser
import os
import re
import redis
import json

def getmysqlconnect():
    config = configparser.ConfigParser()
    config.read('config.ini')
    stage='mysql'
    dbuser=config[stage]['username']
    dbpassw=config[stage]['password']
    dbhost = config[stage]['host']
    dbname = config[stage]['dbname']
    dbconnection = 'mysql+pymysql://'+dbuser+':'+dbpassw+'@'+dbhost+':3306/'+dbname
    return dbconnection