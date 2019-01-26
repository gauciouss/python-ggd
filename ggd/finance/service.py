import logging
from .spider import StockInfo
from ggd.database.sessionFactory import MySQLSessionFactory
from ggd.util.ggdUtil import Profiler
from ggd.util.ggdUtil import FinanceDateUtil
import datetime as dt
import time
import calendar
import ggd.finance.dao
from ggd.finance.models import TWStockQuote
import sys

class FunctionalService:

    log = logging.getLogger()
    gdo = None
    START_QUOTE_DATE = "20100101"    

    def __init__(self, gdo):
        self.gdo = gdo


    
    '''
    回補報價資料
    '''
    def ReverseQuote(self, stk_id = None):
        p = Profiler()
        self.log.info("[START] {cn}.ReverseQuote(), stk_id: {sn}".format(cn = type(self).__name__, sn = stk_id))

        stks = self.gdo.Get_Stock(stk_id)
        
        preStkId = ""
        preDate = ""
        for stk in stks:
            sid =stk["STOCK_ID"]
            si = StockInfo(sid)
            ss = self.gdo.Get_Last_Quote(sid)
            fo = ss.fetchone()
            start = None
            end = dt.datetime.now().strftime("%Y%m%d")
            if fo is None:
                #無該商品報價存在db，從頭開始抓
                start = self.START_QUOTE_DATE                
            else:
                #該商品已有報價存在db中且不是當日(今天已抓過)，從隔一天開始抓                
                if fo["q_date"].strftime("%Y%m%d") != dt.datetime.now().strftime("%Y%m%d"):
                    start = fo["q_date"] + dt.timedelta(days=1)
                
                if start is None:
                    continue
                #要確定盤後才可以抓取
                self.log.info("stk: {s} >> {d} 已抓取過盤後資料，往下一檔前進".format(s = sid, d = start))
                d1 = dt.datetime.combine(start, dt.time())
                d2 = dt.datetime.now().replace(hour = 16, minute = 0, second = 0)     

                self.log.debug("d1: " + d1.isoformat())           
                self.log.debug("d2: " + d2.isoformat()) 
                                
                if d1 > d2:
                    continue

            self.log.debug("to get stk: {id} quotes between {s} and {e}".format(id = sid, s = start, e = end))

            id, qs = si.GetQuote_from_Yahoo(start, end)
            if qs is None:
                continue                    

            lastDateQuote = "select * from TW_STOCK_QUOTE where stk_id = {stk} and q_date = (select max(q_date) from TW_STOCK_QUOTE where stk_id = {stk})".format(stk = id)

            

            beans = []            
            for q in qs:
                quote_date = dt.datetime.strptime(q["date"], "%Y-%m-%d")
                bean = TWStockQuote(
                    stk_id = id,
                    q_date = quote_date,
                    open = float(q["open"]),
                    high = float(q["high"]),
                    low = float(q["low"]),
                    close = float(q["close"]),
                    volumn = int(float(q["volumn"]))
                )

                if preStkId != "" and bean.stk_id == preStkId and bean.q_date == preDate:
                    continue
                else:                    
                    preStkId = id
                    preDate = quote_date
                    beans.append(bean)
            
            self.gdo.saveBeans(beans)

        self.log.info("[END] {cn}.ReverseQuote(), exec TIME: {t} ms., stk_id: {sn}".format(cn = type(self).__name__, t = p.executeTime(), sn = stk_id))

    


        
