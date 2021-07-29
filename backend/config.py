#!/usr/sbin/python
# coding=utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_cors import CORS
from apps.utils.dbconfig import getmysqlconnect
import os

SQLALCHEMY_DATABASE_URI = getmysqlconnect()
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_POOL_RECYCLE = 600
SQLALCHEMY_POOL_SIZE = 200

app = Flask(__name__)
app.config.from_object('config')
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
CORS(app, supports_credentials=True)

db = SQLAlchemy(app=app,session_options={"autoflush":False})
