import time
import calendar
import inspect
import csv
import requests
from io import StringIO

class Profiler:

    start = None

    def __init__(self):
        self.start = time.time()

    def executeTime(self):
        now = time.time()
        t = now - self.start
        return t
    
    def startLog(self, msg = "", *p):
        stack = inspect.stack()
        the_class = stack[1][0].f_locals["self"].__class__
        the_method = stack[1][0].f_code.co_name
        logStr = "[START] {c}.{m}(). ".format(c = the_class, m = the_method)
        logStr = logStr + msg
        if len(p) > 0:
            logStr = logStr.format(*p)
        return logStr
    
    def endLog(self, msg = "", *p):
        stack = inspect.stack()
        the_class = stack[1][0].f_locals["self"].__class__
        the_method = stack[1][0].f_code.co_name
        logStr = "[END] {c}.{m}(), exec TIME: {t} ms. ".format(c = the_class, m = the_method, t = self.executeTime())
        logStr = logStr + msg
        if len(p) > 0:
            logStr = logStr.format(*p)
        return logStr
        
        


class FinanceDateUtil:
    
    '''
    判斷是否當月的最後一天
    '''
    def isLastMonthDay(self, y, m, d):        
        ld = calendar.monthrange(y, m)[1]
        return True if d == ld else False


    def GetHoliday(self, year):
        url = 'https://www.twse.com.tw/holidaySchedule/holidaySchedule?response=csv&queryYear={d}'.format(d = year)
        resp = requests.get(url)
        t = resp.text
        #sp = t.split("\n")
        ##前3行去掉
        f = StringIO(t)
        reader = csv.reader(f, delimiter = ",")
        rs = {}
        i = 0
        year = year + 1911
        for r in reader:
            if i < 2:
                i = i + 1
                continue
            name = r[0].strip()
            date = r[1]            

            ds = date.split("日")
            _d = []
            for d in ds:              
                if d == "":
                    continue  
                d = d.replace("月", "/")                
                d = str(year) + "/" + d                
                _d.append(d)
            rs[name] = _d 
        return rs