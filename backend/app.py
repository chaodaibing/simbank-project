#!/usr/bin/env python
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import db, app
from flasgger import Swagger
from apps.simo import register_simo
import traceback
import apps.utils.log
import logging

logger = logging.getLogger()

def init_app(app):
  template = dict(swaggerUiPrefix='/modifybackend')
  swagger = Swagger(app, template=template)
  register_simo(app)

init_app(app)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=9528, debug=True)
