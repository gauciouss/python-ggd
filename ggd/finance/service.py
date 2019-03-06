import logging
from .spider import StockInfo
from ggd.database.sessionFactory import MySQLSessionFactory
from ggd.util.ggdUtil import Profiler
from ggd.util.ggdUtil import FinanceDateUtil
import datetime as dt
import time
import calendar
import ggd.finance.dao
from ggd.finance.models import TWStockQuote, ExchangeDailyReport
import sys

class FunctionalService:

    log = logging.getLogger()
    gdo = None
    START_QUOTE_DATE = "20100101"    

    def __init__(self, gdo):
        self.gdo = gdo


    def Get_all_stk(self):
        stks = self.gdo.Get_Stock()
        return stks

    
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
                #Yahoo中無該檔股票
                continue

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
            self.Calcute_UpDown(sid)
            self.EWMA(sid)

        self.log.info("[END] {cn}.ReverseQuote(), exec TIME: {t} ms, stk_id: {sn}".format(cn = type(self).__name__, t = p.executeTime(), sn = stk_id))

    '''
    計算漲跌&漲跌幅
    @param stk_id: 股票代碼    
    '''
    def Calcute_UpDown(self, stk_id):        
        p = Profiler()
        self.log.info("[START] {cn}.Calcute_UpDown(), stk_id: {id}".format(cn = type(self).__name__, id = stk_id))
        #取出未計算漲跌的資料
        ls = self.gdo.Get_Uncalcute_Updown(stk_id)  
        #取出最後一筆有計算漲跌的資料      
        updownObj = self.gdo.Get_Last_Updown(stk_id)        
        close = updownObj["close"]
        for obj in ls:
            distance = obj["close"] - close
            updown = distance
            updown_limit = round((distance / close) * 100, 2)
            self.log.debug("stk_id: {id}, q_date: {qd}, updown: {upd}, updown_limit: {updl}".format(id = stk_id, qd = obj["q_date"], upd = updown, updl = updown_limit))
            
            self.gdo.update_updown_value(
                stk_id = stk_id,
                q_date = obj["q_date"].strftime("%Y-%m-%d"),
                updown = updown,
                updown_limit = updown_limit
            )
            close = obj["close"]

        self.log.info("[END] {cn}.Calcute_UpDown(), exec TIME: {t} ms, stk_id: {id}".format(cn = type(self).__name__, id = stk_id, t = p.executeTime()))        

    '''
    計算ewma
    @param stk_id 股票代碼
    '''
    def EWMA(self, stk_id):
        p = Profiler()
        self.log.info("[START] {cn}.EWMA(), stk_id: {sn}".format(cn = type(self).__name__, sn = stk_id))
                
        last_quote_obj = self.gdo.Get_Last_EWMA(stk_id)        
        Ay = last_quote_obj["A"]
        lambdaa = 0.06
        ls = self.gdo.Get_Noncalcute_EWMA(stk_id)                   
        for obj in ls:
            r = obj["updown_limit"]
            Ai = round(pow(r, 2) * lambdaa + Ay * (1-lambdaa), 2)
            ewma = round(pow(Ai*250, 0.5), 2)
            self.gdo.updateEWMA(stk_id, obj["q_date"], Ai, ewma)

    '''
    取得每日買賣日報表
    '''
    def GetExchangeDailyReport(self, stk_id):
        p = Profiler()
        self.log.info("[START] {cn}.GetExchangeDailyReport(), stk_id: {id}".format(cn = type(self).__name__, id = stk_id))
        stk_spider = StockInfo(stk_id)
        #TODO insert data into table
        rs = stk_spider.GetExchangeDaily()
        beans = []
        for r in rs:            
            m = ExchangeDailyReport(
                stk_id = stk_id,
                brokerId = r["brokerId"],
                price = float(r["price"]),
                buy_volumn = int(r["buy_volumn"]),
                sell_volumn = int(r["sell_volumn"]),
                date = '2019/03/06' 
            )            
            beans.append(m)            
        self.gdo.saveBeans(beans)
        self.log.info("[END] {cn}.GetExchangeDailyReport(), exec TIME: {t} ms, stk_id: {id}".format(cn = type(self).__name__, id = stk_id, t = p.executeTime()))
        

                            
    
    '''
    取得連漲d天的股票
    '''
    def Get_Up_Continue_Stk(self, d):
        if d < 1:
            return None
        d = d +1
        ls = []
        date = dt.datetime.now()
        for i in range(d):                   
            date = date + dt.timedelta(days = -1)
            str_date = date.strftime("%Y-%m-%d")
            self.log.debug("date: " + str_date)
            rs = self.gdo.Get_up_Stk(str_date)
            t = []
            for r in rs:
                t.append(r)

            if len(ls) == 0:
                ls = t                
            else:                                
                for r in ls:
                    if r not in rs:
                        ls.remove(r)        


        rs = []
        for obj in ls:
            stk_id = obj[0]
            stkObj = self.gdo.Get_Stock_Info(stk_id).fetchone()
            _stk = {
                "id": stk_id,
                "stk_name": stkObj[1],
                "industry_name": stkObj[2],
                "close": stkObj.close,
                "url": "http://newjust.masterlink.com.tw/z/zc/zcw/zcw1ChgPage_"+ stk_id +".djhtm"                
            }
            rs.append(_stk)

        return rs
