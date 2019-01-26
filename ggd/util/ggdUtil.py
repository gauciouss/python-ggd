import time
import calendar

class Profiler:

    start = None

    def __init__(self):
        self.start = time.time()

    def executeTime(self):
        now = time.time()
        t = now - self.start
        return t


class FinanceDateUtil:
    
    '''
    判斷是否當月的最後一天
    '''
    def isLastMonthDay(self, y, m, d):        
        ld = calendar.monthrange(y, m)[1]
        return True if d == ld else False