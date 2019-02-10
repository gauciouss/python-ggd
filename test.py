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
        return ls

    def test_get_all_stk(self, callback):
        sessionFactory = MySQLSessionFactory(self.sql_cfg)
        sql = "select distinct stk_id from tw_stock_quote"
        session = sessionFactory.GetSession()
        ls = session.execute(sql)
        for obj in ls:
            #self.test_get_first_quote(obj["stk_id"])
            callback(obj["stk_id"])


    def test_get_first_quote(self, stk_id):
        sessionFactory = MySQLSessionFactory(self.sql_cfg)
        sql = "select stk_id, q_date from tw_stock_quote where q_date = (select min(q_date) from tw_stock_quote where stk_id = '{stk_id}') and stk_id = '{stk_id}'"
        sql = sql.format(stk_id = stk_id)
        session = sessionFactory.GetSession()
        ls = session.execute(sql)
        
        for obj in ls:
            #print(obj["q_date"])
            sql2 = "update tw_stock_quote set A = pow(updown_limit, 2) * 0.06 where stk_id = '{stk_id}' and q_date = '{qd}'"
            sql2 = sql2.format(stk_id = stk_id, qd = obj["q_date"])            
            session.execute(sql2)
            session.commit()
        session.close()
            

    def test_calcute_ewma(self, stk_id):
        sessionFactory = MySQLSessionFactory(self.sql_cfg)
        session = sessionFactory.GetSession()
        sql = "select * from tw_stock_quote where stk_id = '{stk_id}' order by q_date"
        sql = sql.format(stk_id = stk_id)
        ls = session.execute(sql)
        i = 1
        A = 0
        for obj in ls:
            id = obj["stk_id"]
            qd = obj["q_date"]
            if i == 1:
                A = obj["A"]                
                i = i + 1
            else:
                rate = obj["updown_limit"]
                A = self.A(rate, A)

            ewma = pow(A * 250, 0.5)    

            sql2 = "update tw_stock_quote set A = {A}, ewma = {ewma} where stk_id = '{id}' and q_date = '{qd}'"
            sql2 = sql2.format(A = A, ewma = ewma, id = id, qd = qd)
            session.execute(sql2)
            session.commit()
            


            
    
        
    def A(self, r, xi):
        a = pow(r, 2) * 0.06 + xi * (1-0.06)        
        return a

                

            

            




mt = Mytest()
mt.test_get_all_stk(mt.test_calcute_ewma)
