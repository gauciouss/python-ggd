import logging
import logging.handlers
from logging.handlers import RotatingFileHandler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from ggd.database.sessionFactory import MySQLSessionFactory
from ggd.finance.dao import GGDDao as gdo
from ggd.finance.service import FunctionalService
from ggd.finance.spider import StockInfo



#loggin 設定
logging.basicConfig(level=logging.DEBUG,
    #format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    format = "[level:%(levelname)s-file:%(filename)s-lineno:%(lineno)d] %(asctime)s %(message)s",
    datefmt='%m-%d %H:%M',        
    handlers = [logging.FileHandler('my.log', 'a', 'utf-8'), 
    RotatingFileHandler('my.log')]
)

#sql設定
sql_cfg = {
    'account': 'root',
    'password': '12345678',
    'ip': '192.168.194.128',
    'port': '3306',
    'database': 'ggd',
    'poolsize': 20,
    'max_overflow': -1

}



sessionFactory = MySQLSessionFactory(sql_cfg)
dao = gdo(sessionFactory) 
service = FunctionalService(dao)
service.ReverseQuote();


