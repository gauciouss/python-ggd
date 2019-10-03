# -*- coding: UTF-8 -*-
import logging
import logging.handlers
from logging.handlers import TimedRotatingFileHandler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from ggd.database.sessionFactory import MySQLSessionFactory
from ggd.finance.dao import GGDDao as gdo
from ggd.finance.service import FunctionalService
from ggd.finance.spider import StockInfo
from ggd.util.ggdUtil import Profiler
import time



#loggin 設定
logging.basicConfig(level=logging.DEBUG,
    #format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    format = "[level:%(levelname)s-file:%(filename)s-lineno:%(lineno)d] %(asctime)s %(message)s",
    datefmt='%m-%d %H:%M:%S',        
    handlers = [        
        TimedRotatingFileHandler('rotate.log', when = "d", backupCount=5)
    ]
)

#sql設定
sql_cfg = {
    'account': 'finance',
    'password': '1234',
    'ip': '192.168.194.128',
    'port': '3306',
    'database': 'finance',
    'poolsize': 20,
    'max_overflow': -1
}



sessionFactory = MySQLSessionFactory(sql_cfg)
dao = gdo(sessionFactory) 
service = FunctionalService(dao)
cmd = input("input command: ")
if cmd == "1":
    print("開始執行回補")
    service.ReverseQuote()
elif cmd == "2":
    d = 4
    print("查詢連漲{d}天的商品".format(d = d))      
    ls = service.Get_Up_Continue_Stk(d)    
    for obj in ls:                
        if(obj["close"] >= 20):
            print(obj)
elif cmd == "3":
    print("開始計算漲跌")
    stks = dao.Get_Stock()
    for stk in stks:
        service.Calcute_UpDown(stk["STOCK_ID"])
elif cmd == "4":
    print("開始計算EWMA")
    stks = dao.Get_Stock()
    for stk in stks:
        service.EWMA(stk["STOCK_ID"])    
elif cmd == "5":
    print("開始取得買賣日報表")
    #d = datetime.now().strftime("%Y%m%d")
    d = input("指定回補日期：")
    d = datetime.now().strftime("%Y%m%d") if d == "" else d
    stk_id = input("指定ID回補：")
    if stk_id == "":
        stks = dao.Get_Stock()
        for stk in stks:
            service.GetExchangeDailyReport(stk["STOCK_ID"], d)
    else:
        service.GetExchangeDailyReport(stk_id, d)
else:
    print("查無指令")    


