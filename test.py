import unittest
import logging
import csv
from datetime import datetime as dt
from ggd.finance.spider import StockInfo
from ggd.finance.dao import GGDDao as gdo
from ggd.database.sessionFactory import MySQLSessionFactory
from logging.handlers import RotatingFileHandler

class Mytest(unittest.TestCase):



        #loggin 設定
    logging.basicConfig(level=logging.DEBUG,
        #format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        format = "[level:%(levelname)s-file:%(filename)s-lineno:%(lineno)d] %(asctime)s %(message)s",
        datefmt='%m-%d %H:%M',        
        handlers = [logging.FileHandler('my.log', 'w', 'utf-8'), 
        RotatingFileHandler('unit-test.log')]
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


    log = logging.getLogger()

    def test(self):
        self.log.debug('AAAAAAA')


    def parseListCSV(self):
        industrys = {}
        with open('/Users/heliwei/Desktop/t187ap03_L.csv', newline='') as csvFile:
            rows = csv.DictReader(csvFile)
            dd = []            
            for r in rows:                                 
                ind = r["產業別"]
                if ind in dd:
                    continue
                else:
                    dd.append(ind)
            
            
            k = 1
            for d in dd:
                industrys[d] = k
                k = k + 1
        
        sqls = []
        with open('/Users/heliwei/Desktop/t187ap03_L.csv', newline='') as csvFile:
            rows = csv.DictReader(csvFile)
            for r in rows:
                s = "insert into TW_STOCK_LIST (STOCK_ID, COMP_NAME, STOCK_NAME, FOREIGN_COUNTRY_REGISTERED, INDUSTRY, ADDRESS, TAX_ID_NUMBER, CHAIRMAN, GENERAL_MANAGER, SPOKES_MAN, ESTABLISHMENT_DATE, LIST_DATE, CAPITAL_AMOUNT, PRIVATE_EQUITY, PREFERED_EQUITY) VALUES ('{STOCK_NO}', '{COMP_NAME}', '{STOCK_NAME}', '{FOREIGN_COUNTRY_REGISTERED}', '{INDUSTRY}', '{ADDRESS}', '{TAX_ID_NUMBER}', '{CHAIRMAN}', '{GENERAL_MANAGER}', '{SPOKES_MAN}', '{ESTABLISHMENT_DATE}', '{LIST_DATE}', '{CAPITAL_AMOUNT}', '{PRIVATE_EQUITY}', '{PREFERED_EQUITY}');"
                industry_id = industrys[r["產業別"]]
                sql = s.format(STOCK_NO = r["公司代號"].strip(), COMP_NAME=r["公司名稱"].strip(), STOCK_NAME=r["公司簡稱"].strip(), FOREIGN_COUNTRY_REGISTERED=r["外國企業註冊地國"].strip(), INDUSTRY=industry_id, ADDRESS=r["住址"].strip(), TAX_ID_NUMBER=r["營利事業統一編號"].strip(), CHAIRMAN=r["董事長"].strip(), GENERAL_MANAGER=r["總經理"].strip(), SPOKES_MAN=r["發言人"].strip(), ESTABLISHMENT_DATE=r["成立日期"], LIST_DATE=r["上市日期"], CAPITAL_AMOUNT=r["實收資本額"], PRIVATE_EQUITY=r["私募股數"], PREFERED_EQUITY=r["特別股"])
                sqls.append(sql)
        
        with open('/Users/heliwei/Desktop/sql.txt', 'a') as f:
            for sql in sqls:
                f.write(sql)
                f.write("\n")

    def test_get_all_quotes(self):
        sessionFactory = MySQLSessionFactory(self.sql_cfg)
        dao = gdo(sessionFactory) 
        ls = dao.Get_Quotes(start = "20190101", end = "20190110")
        for stk in ls:
            print(stk)

    
        

                

            

            




mt = Mytest()
#mt.parseListCSV()
#print(dt.now().strftime("%m"))
#print("{:02d}".format(1))

#si = StockInfo("2330")
#qs = si.GetQuote_from_Yahoo("20181201", "20181231")
#for q in qs:
    #print(q["date"]) 


mt.test_get_all_quotes()

