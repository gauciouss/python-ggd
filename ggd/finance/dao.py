import logging
from .spider import StockInfo
from ggd.database.sessionFactory import MySQLSessionFactory
from ggd.util.ggdUtil import Profiler
from ggd.finance.models import TWSEStkQuote
import datetime
import calendar

class GGDDao:

    log = logging.getLogger()
    sessionFactory = None

    def __init__(self, sessionFactory):
        self.sessionFactory = sessionFactory

    def saveBeans(self, beans):
        p = Profiler()
        self.log.info("[START] {cn}.saveBeans(), beans count: {c}".format(cn = type(self).__name__, c = len(beans)))
        session = None;
        try:
            session = self.sessionFactory.GetSession()
            session.add_all(beans)
            session.commit()                        
        except Exception as e:
            self.log.error(str(e))
        finally:
            session.close()
        self.log.info("[END] {cn}.saveBeans(), exec TIME: {t} ms.".format(cn = type(self).__name__, t = p.executeTime()))
    
    '''
    取得證券商品資訊
    @param stk_no 證券商品代碼，若為None則回傳全部商品
    '''
    def Get_Stock(self, stk_id = None):
        p = Profiler()
        self.log.info("[START] {cname}.Get_Stock(), stk_id: {stk_id}".format(cname = type(self).__name__, stk_id = stk_id))
        
        sql = "select * from TW_STOCK_LIST"        
        if stk_id is not None:
            sql = sql + (" where STOCK_ID = " + stk_id)
        
        self.log.debug("exec sql statement: {sql}".format(sql = sql));
        session = self.sessionFactory.GetSession()
        stk_list = session.execute(sql)
        session.close()
        self.log.info("[END] {cname}.Get_Stock(), exec TIME: {t} ms., stk_no: {sn}".format(cname = type(self).__name__, t = p.executeTime(), sn = stk_id))
        return stk_list

    
    '''
    取得資料庫存在的證券商品最後的報價是哪一天
    @param stk_no 證券商品代碼
    '''
    def Get_Last_Quote(self, stk_id):
        p = Profiler()
        self.log.info("[START] {cname}.Get_Last_Quote(), stk_no: {sn}".format(cname = type(self).__name__, sn = stk_id))        
        sql = "select * from TW_STOCK_QUOTE where stk_id = {stk} and q_date = (select max(q_date) from TW_STOCK_QUOTE where stk_id = {stk}) ".format(stk = stk_id)        
        self.log.debug("query last date sql: " + sql)
        session = self.sessionFactory.GetSession()
        stk_list = session.execute(sql)
        session.close()
        self.log.info("[END] {cname}.Get_Last_Quote(), exec TIME: {t} ms., stk_no: {sn}".format(cname = type(self).__name__, t = p.executeTime(), sn = stk_id))
        return stk_list


    '''
    取得報價資訊
    @param start, end: 起迄時間，格式type == datetime
    @param stk_id: 股票代碼，可傳1..*的(list格式)，若不傳則回傳all
    '''
    def Get_Quotes(self, start, end, stk_id = None):
        p = Profiler()        
        self.log.info("[START] {cn}.Get_Quotes(), start: {st}, end: {et}, stk_id: {s}".format(cn = type(self).__name__, st = start, et = end, s = stk_id))
        sql = "select * from view_tw_stock_quote where q_date between {s} and {e} "
        
        if stk_id is not None:
            s = ""
            if type(stk_id).__name__ == "list":
                s = ",".join(stk_id)
            elif type(stk_id).__name__ == "str":
                s = stk_id
            sql = sql + (" and stk_id = " + s)
        sql = sql + " order by stk_id, q_date "
        sql = sql.format(s = start, e = end)
        self.log.debug("sql: " + sql)
        session = self.sessionFactory.GetSession()
        ls = session.execute(sql)
        session.close()
        self.log.info("[END] {cn}.GetQuotes(), exec TIME: {t} ms, start: {st}, end: {et}, stk_id: {stk}".format(cn = type(self).__name__, st = start, et = end, stk = stk_id, t = p.executeTime()))
        return ls


        
        

    