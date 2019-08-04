import logging
from logging.handlers import TimedRotatingFileHandler
from ggd.module.TwStock import TWStockModule, TWStockDao
from ggd.database.sessionFactory import MySQLSessionFactory
from ggd.finance.service import FunctionalService
from ggd.util.ggdUtil import Profiler
from ggd.util.ggdUtil import FinanceDateUtil
import sys
from datetime import datetime as dt


logging.basicConfig(level=logging.DEBUG,
    #format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    format = "[level:%(levelname)s-file:%(filename)s-lineno:%(lineno)d] %(asctime)s %(message)s",
    datefmt='%m-%d %H:%M:%S',        
    handlers = [        
        TimedRotatingFileHandler('rotate.log', when = "d", backupCount=5)
    ]
)

sql_cfg = {
    'account': 'finance',
    'password': '1234',
    'ip': '192.168.194.128',
    'port': '3306',
    'database': 'finance',
    'poolsize': 20,
    'max_overflow': -1
}

log = logging.getLogger()
cmd = sys.argv[1]

p = Profiler()
log.info("cmd: " + cmd)
if cmd == "1":
    log.info("開始執行回補")
    stk_id = sys.argv[2] if len(sys.argv) >= 3 else ""
    if stk_id == "":
        log.info("未輸入symbol id，執行全商品回補")
        dao = TWStockDao()
        rs = dao.Get_All_Stocks()
        for r in rs:
            stk_id = r.STOCK_ID
            tws = TWStockModule(stk_id)
            tws.RevertQuote()
    else:
        tws = TWStockModule(stk_id)
        tws.RevertQuote()    
elif cmd == "2":
    log.info("開始計算漲跌, ewma")
    dao = TWStockDao()
    rs = dao.Get_All_Stocks()
    #service = FunctionalService(dao)
    #for stk in rs:
    #    service.Calcute_UpDown(stk["STOCK_ID"])
    #    service.EWMA(stk["STOCK_ID"])
    #TODO
elif cmd == "3":
    log.info("開始取得買賣日報表")
    d = sys.argv[2] if len(sys.argv) >= 3 else dt.now().strftime("%Y%m%d")
    stk_id = sys.argv[3] if len(sys.argv) >= 4 else ""
    dao = TWStockDao()
    
    if stk_id == "":        
        rs = dao.Get_All_Stocks()
        for r in rs:
            module = TWStockModule(r.STOCK_ID)
            module.GetExangeDailyFromWantgoo(d)
    else:
        module = TWStockModule(stk_id)
        rs = module.GetExangeDailyFromWantgoo(d)
        for r in rs:
            c1 = r["券商名稱"]
            bq1 = r["買量"]
            sq1 = r["賣量"]
            bp1 = r["買價"]
            sp1 = r["賣價"]            
            overbs1 = r["買賣超"]
            avg1 = r["均價"]

            c2 = r["券商名稱2"]
            bq2 = r["買量2"]
            sq2 = r["賣量2"]
            bp2 = r["買價2"]
            sp2 = r["賣價2"]
            overbs2 = r["買賣超2"]
            avg2 = r["均價2"]
            
            if c1 is not None:                
                id = c1[-5:-1]
                name = c1[:(len(c1) - 6)]                
                dao.Save_Daily_Exchange(stk_id, d, id, name, bq1, sq1, bp1, sp1, overbs1, avg1)
            
            if c2 is not None:
                id = c2[-5:-1]
                name = c2[:(len(c2) - 6)]                
                dao.Save_Daily_Exchange(stk_id, d, id, name, bq2, sq2, bp2, sp2, overbs2, avg2) 
elif cmd == "4":
    log.info("開始取得當年度休市日")
    dao = TWStockDao()    
    year = dt.now().year
    year = year - 1911 #轉成明國年
    dao.SaveHoliday(year)
    
    


log.info("cmd: " + cmd + " 執行結束，共花費: "+ str(p.executeTime()) + " ms.")
