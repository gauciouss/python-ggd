import logging
from .spider import StockInfo
from ggd.database.sessionFactory import MySQLSessionFactory
from ggd.util.ggdUtil import Profiler
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

    def updateBeans(self, key, value):
        p = Profiler()
        self.log.info("[START] {cn}.updateBeans()".format(cn = type(self).__name__))
        session = None
        try:
            session = self.sessionFactory.GetSession()
            #更新資料 
            session.filter(key).update(value)
            session.commit()
        except Exception as e:
            self.log.error(str(e))
        finally:
            session.close()

        self.log.info("[END] {cn}.updateBeans(), exec TIME: {t} ms.".format(cn = type(self).__name__, t = p.executeTime()))

    def update_updown_value(self, stk_id, q_date, updown, updown_limit):
        p = Profiler()
        self.log.info("[START] {cn}.update_updown_value(), stk_id: {id}, q_date: {qd}, updown: {u}, updown_limit: {ul}".format(cn = type(self).__name__, id = stk_id, qd = q_date, u = updown,  ul = updown_limit))
        sql = "update tw_stock_quote set updown = {u}, updown_limit = {ul} where stk_id = '{id}' and q_date = '{qd}'".format(u = updown, ul = updown_limit, id = stk_id, qd = q_date) 
        self.log.debug("update updown sql: " + sql)
        session = self.sessionFactory.GetSession()
        session.execute(sql)
        session.commit()
        session.close()
        self.log.info("[end] {cn}.update_updown_value(), stk_id: {id}, q_date: {qd}, updown: {u}, updown_limit: {ul}, exec TIME: {t}".format(cn = type(self).__name__, id = stk_id, qd = q_date, u = updown,  ul = updown_limit, t = p.executeTime()))
        pass
    
    '''
    取得證券商品資訊
    @param stk_no 證券商品代碼，若為None則回傳全部商品
    '''
    def Get_Stock(self, stk_id = None):
        p = Profiler()
        self.log.info("[START] {cname}.Get_Stock(), stk_id: {stk_id}".format(cname = type(self).__name__, stk_id = stk_id))
        
        sql = "select distinct a.* from TW_STOCK_LIST a inner join tw_stock_quote b on a.STOCK_ID = b.stk_id where a.DELISTING_DATE is null "        
        if stk_id is not None:
            sql = sql + (" and a.STOCK_ID = " + stk_id)
        
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
        sql = "select * from tw_stock_quote where stk_id = {stk} and q_date = (select max(q_date) from tw_stock_quote where stk_id = {stk}) ".format(stk = stk_id)        
        self.log.debug("query last date sql: " + sql)
        session = self.sessionFactory.GetSession()
        stk_list = session.execute(sql)
        session.close()
        self.log.info("[END] {cname}.Get_Last_Quote(), exec TIME: {t} ms., stk_no: {sn}".format(cname = type(self).__name__, t = p.executeTime(), sn = stk_id))
        return stk_list

    
    '''
    取出尚未計算漲跌的資料
    @param stk_id: 股票代碼
    '''
    def Get_Uncalcute_Updown(self, stk_id):
        p = Profiler()
        self.log.info("[START] {cn}.Calcute_UpDown(), stk_id: {id}".format(cn = type(self).__name__, id = stk_id))
        sql1 = "select * from tw_stock_quote where stk_id = '{id}' and updown is null order by q_date".format(id = stk_id)        
        session = self.sessionFactory.GetSession()
        ls = session.execute(sql1)        
        self.log.info("[END] {cn}.Calcute_UpDown(), exec TIME: {t} ms, stk_id: {id}".format(cn = type(self).__name__, t = p.executeTime(), id = stk_id))
        return ls

    '''
    取出最後一筆計算過漲跌的資料
    @param stk_id: 股票代碼
    '''
    def Get_Last_Updown(self, stk_id):
        p = Profiler()
        self.log.info("[START] {cn}.Get_Last_Updown(), stk_id: {id}".format(cn = type(self).__name__, id = stk_id))       
        sql = "select * from tw_stock_quote where stk_id = '{id}' and updown is not null order by q_date desc limit 1".format(id = stk_id)
        session = self.sessionFactory.GetSession()
        rs = session.execute(sql).fetchone()
        self.log.info("[END] {cn}.Get_Last_Updown(), exec TIME: {t} ms, stk_id: {id}".format(cn = type(self).__name__, t = p.executeTime(), id = stk_id)) 
        return rs


    '''
    取得報價資訊
    @param start, end: 起迄時間，格式type == datetime
    @param stk_id: 股票代碼，可傳1..*的(list格式)，若不傳則回傳all
    '''
    def Get_Quotes(self, start, end, stk_id = None):
        p = Profiler()        
        self.log.info("[START] {cn}.Get_Quotes(), start: {st}, end: {et}, stk_id: {s}".format(cn = type(self).__name__, st = start, et = end, s = stk_id))
        sql = "select * from tw_stock_quote where q_date between {s} and {e} "
        
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

    '''
    取出尚未計算ewma的商品
    @param stk_id 股票代號
    '''
    def Get_Noncalcute_EWMA(self, stk_id):
        p = Profiler()
        self.log.info("[START] {cn}.Get_Noncalcute_EWMA(), stk_id: {id}".format(cn = type(self).__name__, id = stk_id))
        sql = "select * from tw_stock_quote where stk_id = '{id}' and ewma is null order by q_date desc".format(id = stk_id)                
        session = self.sessionFactory.GetSession()
        ls = session.execute(sql)
        session.close()
        self.log.info("[END] {cn}.Get_Noncalcute_EWMA(), exec TIME: {t} ms, stk_id: {id}".format(cn = type(self).__name__, t = p.executeTime(), id = stk_id))
        return ls

    '''
    取出最後一筆已計算ewma的資料
    @param stk_id 股票代號
    '''
    def Get_Last_EWMA(self, stk_id):
        p = Profiler()
        self.log.info("[START] {cn}.Get_Last_EWMA(), stk_id: {id}".format(cn = type(self).__name__, id = stk_id))
        sql = "select * from tw_stock_quote where stk_id = '{id}' and ewma is not null order by q_date desc limit 1".format(id = stk_id)        
        session = self.sessionFactory.GetSession()
        rs = session.execute(sql).fetchone()
        session.close()
        self.log.info("[END] {cn}.Get_Last_EWMA(), exec TIME: {t} ms, stk_id: {id}".format(cn = type(self).__name__, t = p.executeTime(), id = stk_id))
        return rs

    def updateEWMA(self, stk_id, q_date, A, ewma):
        p = Profiler()
        self.log.info("[START] {cn}.updateEWMA(), stk_id: {id}, q_date: {d}, A: {A}, EWMA: {ewma}".format(cn = type(self).__name__, id = stk_id, d = q_date, A = A, ewma = ewma))
        sql = "update tw_stock_quote set A = {A}, ewma = {ewma} where stk_id = '{s}' and q_date = '{d}'".format(A = A, ewma = ewma, s = stk_id, d = q_date)
        session = self.sessionFactory.GetSession()
        session.execute(sql)
        session.commit()
        session.close()
        self.log.info("[end] {cn}.updateEWMA() exec TIME: {t} ms, stk_id: {id}, q_date: {d}, A: {A}, EWMA: {ewma}".format(cn = type(self).__name__, id = stk_id, d = q_date, A = A, ewma = ewma, t = p.executeTime()))
    

    '''
    取出d日有漲/跌的證券商品
    '''
    def Get_up_Stk(self, d, up_or_down = 1):
        p = Profiler()
        self.log.info("[START] {cn}.Get_up_Stk(), date: '{date}', up_or_down: {u}".format(cn = type(self).__name__, date = d, u = up_or_down))
        sql = ""
        if 1 >= 0:
            sql = "select * from tw_stock_quote where updown_limit >= 0"
        else:
            sql = "select * from tw_stock_quote where updown_limit < 0"
        sql = sql + " and q_date = '{d}'"
        sql = sql.format(d = d)
        self.log.debug("sql: " + sql)
        session = self.sessionFactory.GetSession()
        rs = session.execute(sql)
        session.close()
        self.log.info("[END] {cn}.Get_up_Stk(), exec TIME: {t} ms, date: '{date}', up_or_down: {u}".format(cn = type(self).__name__, date = d, u = up_or_down, t = p.executeTime()))
        return rs

    '''
    取得商品基本檔&
    '''
    def Get_Stock_Info(self, stk_id):
        p = Profiler()
        self.log.info("[START] {cname}.Get_Stock_Info(), stk_id: {stk_id}".format(cname = type(self).__name__, stk_id = stk_id))
        
        sql = """
                select STOCK_ID, STOCK_NAME, NAME, q.close, q.q_date
	                from TW_STOCK_LIST a 
		            inner join TW_STOCK_INDUSTRY b on a.INDUSTRY = b.SERIAL_NO
                    inner join (select stk_id, close, q_date from tw_stock_quote where stk_id = '{id}' order by q_date desc limit 1) q on a.STOCK_ID = q.stk_id   
                    where a.STOCK_ID = '{id}'
                    order by b.SERIAL_NO, a.STOCK_ID, close                
	          """
              
        sql = sql.format(id = stk_id)
        
        self.log.debug("exec sql statement: {sql}".format(sql = sql));
        session = self.sessionFactory.GetSession()
        stk_list = session.execute(sql)
        session.close()
        self.log.info("[END] {cname}.Get_Stock_Info(), exec TIME: {t} ms., stk_no: {sn}".format(cname = type(self).__name__, t = p.executeTime(), sn = stk_id))
        return stk_list

    