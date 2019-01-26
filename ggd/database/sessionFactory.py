from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from mysql import connector
import logging

class MySQLSessionFactory:

    engine = None
    log = logging.getLogger()

    def __init__(self, cfg):
        db_str = 'mysql+mysqlconnector://{account}:{password}@{ip}:{port}/{db}'.format(account = cfg['account'], password = cfg['password'], ip = cfg['ip'], port = cfg['port'], db = cfg['database'])
        self.log.info('database connection str: {dbstr}'.format(dbstr = db_str))
        self.engine = create_engine(db_str, poolclass=StaticPool, pool_recycle=3600)
    
    def GetSession(self):
        dbsession = sessionmaker(bind = self.engine)
        session = dbsession()
        return session
