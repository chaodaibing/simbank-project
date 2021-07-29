from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Text, DateTime,\
    and_, or_, SmallInteger, Float, DECIMAL, desc, asc, Table, join, event
from config import db

#########################人员信息表############################################################
class Board(db.Model):
    __tablename__='sc_board'
    id = Column('id',db.Integer)
    actual_cnt = Column('actual_cnt',db.Integer)
    sn = Column('sn',db.String(50),primary_key=True)    
    board_version = Column('board_version',db.String(50))
    ip_address = Column('ip_address',db.String(100))
    logic_addr = Column('logic_addr',db.Integer)
    use_status = Column('use_status',db.Integer)
    updated_date = Column('updated_date',db.DateTime)
    def to_json(self):
        return {
            'id':self.id,
            'actual_cnt':self.actual_cnt,
            'sn': self.sn,
            'board_version': self.board_version.replace('\x00',''),
            'ip_address': self.ip_address,
            'logic_addr': self.logic_addr,
            'use_status': self.use_status,
            'updated_date': self.updated_date,
            'check_loading': False,
            'upgrade_loading':False
        }

class Blade(db.Model):
    __tablename__='sc_blade'
    id = Column('id',db.Integer,primary_key=True)             #注意设置primary_ke为True的字段，查询结果会自动去重
    stick_id = Column('logic_addr',db.Integer)                #卡条位置
    board_sn = Column('board_sn',db.String(50))
    stick_version = Column('blade_version',db.String(50))
    board_id = Column('board_addr',db.Integer)                #对应的board的ID
    updated_date = Column('updated_date',db.DateTime)
    state = Column('state',db.Integer)
    def to_json(self):
        return {
            'id':self.id,
            'stick_id':self.stick_id,
            'stick_version': self.stick_version.replace('\x00',''),
            'board_sn': self.board_sn,
            'board_id': self.board_id,
            'updated_date': self.updated_date,
            'state':self.state,
            'check_loading': False,
            'upgrade_loading':False
        }


db.create_all()