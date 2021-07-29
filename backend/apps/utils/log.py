# -*- coding:utf-8 -*-
import logging
from logging.handlers import TimedRotatingFileHandler


def set_logger():
    # logger
    logger = logging.getLogger()
    formater = logging.Formatter('%(asctime)s %(name)s %(funcName)s %(lineno)d [%(levelname)s] : %(message)s')
    # fh = TimedRotatingFileHandler('log/backend.log', when='MIDNIGHT', interval=1, backupCount=10)
    # fh.setFormatter(formater)
    # logger.addHandler(fh)
    # 控制台
    sh = logging.StreamHandler()
    sh.setFormatter(formater)
    logger.addHandler(sh)
    # sh.setLevel(logging.WARNING)
    # log级别
    logger.setLevel(logging.INFO)


set_logger()
