from sqlalchemy import create_engine, MetaData, Column, VARCHAR, INT, BIGINT, FLOAT, REAL, ForeignKey, Table, collate, BOOLEAN
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from credentials.credentials import *

base = declarative_base()
engine = create_engine('mysql+pymysql://{0}:{1}@127.0.0.1/{2}?host=127.0.0.1?port={3}/charset=utf8/'.format(DBUNAME, DBPASS, DB, DBPORT))
# create a configured "Session" class
conn = engine.connect()
Session = sessionmaker(bind=conn)
# create a Session
session = Session()
"""
def metaModels(engine):
    meta = MetaData(engine)
    # Register users, txs, gambles, and counter to metadata
    t1 = Table('stakes', meta,
               Column('tid', INT, primary_key=True),
               Column('hash', VARCHAR(100)),
               Column('amount', REAL),
               Column('nUsers', BIGINT, default=0),
               mysql_engine='InnoDB',
               mysql_charset='utf8mb4'
               )
    meta.create_all()"""


def metaModels(engine):
    meta = MetaData(engine)
    #
    t2 = Table('maturing', meta,
               Column('mid', BIGINT, primary_key=True),
               Column('tid', BIGINT, default=0),
               Column('uid', BIGINT, default=0),
               Column('amount', REAL, default=0),
               Column('time', BIGINT, default=0),
               Column('nUsers', BIGINT, default=0),
               mysql_engine='InnoDB',
               mysql_charset='utf8mb4'
               )
    meta.create_all()


metaModels(engine)