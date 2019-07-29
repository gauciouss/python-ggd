import logging
import requests
from bs4 import BeautifulSoup
import csv
import pandas_datareader.data as web
import datetime
import traceback
import time
from ggd.util.ggdUtil import Profiler
import sys
import io
import json

class TWStockSummaryInfo:

    log = logging.getLogger()

    #取得三大法人買賣超日報表
    def Get_Over_BS_Daily(self, date, callback, type='ALLBUT0999'):
        url = 'http://www.twse.com.tw/fund/T86'
        params = dict(
            response = 'json',
            selectType = type,
            date = date
        )
        resp = requests.get(url, params)
        json = resp.json()
        stat = json['stat']
        self.log.info('stat: %s', stat)
        if stat != 'OK':
            return None
        else:
            data = json['data']
            rs = []
            for d in data:
                p = {}
                p['STK_ID'] = d[0]
                p['V_DATE'] = date
                p['PRC_BUY_VOLUMN'] = d[2].replace(',', '')
                p['PRC_SELL_VOLUMN'] = d[3].replace(',', '')
                p['PRC_OVER_BUY_SELL_VOLUMN'] = d[4].replace(',', '')
                p['FORRIGN_SELF_EMPLOYED_BUY_VOLUMN'] = d[5].replace(',', '')
                p['FOREIGN_SELF_EMPLOYED_SELL_VOLUMN'] = d[6].replace(',', '')
                p['FOREIGN_SELF_EMPLOYED_OVER_BUY_SELL_VOLUMN'] = d[7].replace(',', '')
                p['SITCA_BUY_VOLUMN'] = d[8].replace(',', '')
                p['SITCA_SELL_VOLUMN'] = d[9].replace(',', '')
                p['SITCA_OVER_BUY_SELL_VOLUMN'] = d[10].replace(',', '')
                p['SELF_EMPLOYED_OVER_BUY_SELL_VOLUMN'] = d[11].replace(',', '')
                p['SELF_EMPLOYED_BUY_VOLUMN_SELF'] = d[12].replace(',', '')
                p['SELF_EMPLOYED_SELL_VOLUMN_SELF'] = d[13].replace(',', '')
                p['SELF_EMPLOYED_OVER_BUY_SELL_SELF'] = d[14].replace(',', '')
                p['SELF_EMPLOYED_BUY_VOLUMN_RISK'] = d[15].replace(',', '')
                p['SELF_EMPLOYED_SELL_VOLUMN_RISK'] = d[16].replace(',', '')
                p['SELF_EMPLOYED_OVER_BUY_SELL_RISK'] = d[17].replace(',', '')
                p['TOTAL_OVER_BUY_SELL_VOLUMN'] = d[18].replace(',', '')
                rs.append(p)
            if callback is not None:
                callback(rs)
            else:
                return rs
        
        


class StockInfo:

    log = logging.getLogger()
    stock_no = ''

    #抓報價時，若被擋的話，重複的次數
    MAX_REPEAT_TIMES = 2
    
    #買賣日報表連結
    EXCHANGE_DAILY_URL = 'http://bsr.twse.com.tw/bshtm/'

    #證交所每日收盤行情
    STOCK_DAY = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={d}&stockNo={stk}'

    def __init__(self, stock_no):
        self.log.info('new instance >>> stock_no: ' + str(stock_no))
        self.stock_no = stock_no


    #從TWSE抓報價
    def Get_Quote_from_TWSE(self, yyyymm, callback = None):
        p = Profiler()
        self.log.info('[START] {cname}.Get_Quote_from_TWSE(), stk_id: {stk}, date: {d}'.format(cname = type(self).__name__, stk = self.stock_no, d = yyyymm))
        ymd = yyyymm + '01'
        url = self.STOCK_DAY.format(d = ymd, stk = self.stock_no)
        try:
            resp = requests.get(url)        
            json = resp.json()
            self.log.debug(json)
            stat = json['stat']
            self.log.debug('url: {url}, stat: {stat}'.format(url = url, stat = stat))
            if stat != 'OK':
                self.log.info('stk: {stk}, ymd: {ymd} IS NOT EXIST'.format(stk = self.stock_no, ymd = ymd))
                return None
            else:
                resp_date = json['date']
                data_json = json['data']
                self.log.debug('date: {d}, data size: {s}'.format(s = len(data_json), d = resp_date))
                rs = []
                for data in data_json:
                    dt = data[0]
                    volumn = data[1]
                    price = data[2]
                    o = data[3]
                    h = data[4]
                    l = data[5]
                    c = data[6]
                    p_distance = data[7] if data[7].find("X") == -1 else 0                    
                    d_count = data[8]
                    dd = {'date': dt, 'volumn': volumn, 'price': price, 'open': o, 'high': h, 'low': l, 'close': c, 'p_distance': p_distance, 'total_count': d_count}
                    rs.append(dd)

                if(callback is not None):
                    callback(self.stock_no, rs)
                else:
                    return self.stock_no, rs
        except:
            self.log.error('TESE拒絕連線，等待' + str(self.MAX_REPEAT_TIMES) + '分鐘後再試')
            time.sleep(self.MAX_REPEAT_TIMES*60)
            self.Get_Quote_from_TWSE(yyyymm, callback)

        

    

    #取得每檔股票開高低收
    def GetQuote_from_Yahoo(self, start, end, callback = None):
        pr = Profiler()
        self.log.info('[START] {cname}.GetQuote_from_Yahoo(), start: {start}, end: {end}'.format(cname = type(self).__name__, start = start, end = end))
        try:
            f = web.DataReader(self.stock_no + '.TW', 'yahoo', start, end)            
            fcsv = f.to_csv()                   
            rs = []            
            i = 0
            sp = fcsv.splitlines()
            for row in sp:
                self.log.debug('row: ' + row)
                if i == 0:
                    i = i + 1
                    continue
                if ',,,' in row:
                    self.log.info('empty data: ' + row)
                    continue
                d = row.split(',')
                p = {}
                p['date'] = d[0]
                p['high'] = d[1]
                p['low'] = d[2]
                p['open'] = d[3]
                p['close'] = d[4]
                p['volumn'] = d[5]
                p['adj_close'] = d[6]
                rs.append(p)
            
            self.log.info("[END] {cn}.GetQuote_from_Yahoo(), exec TIME: {t} ms, start: {s}, end: {e}, stk_id: {id}".format(cn = type(self).__name__, t = pr.executeTime(), s = start, e = end, id = self.stock_no))

            if callback is not None:
                callback(self.stock_no, rs)
            else:
                return self.stock_no, rs
        except Exception as e:
            msg = str(e)
            self.log.error(msg)

            if msg.find("No data fetched for symbol") >= 0:
                return None, None 
            else:
                self.log.error('happen error. repeat get data, stock_no: ' + self.stock_no + ', repeat times: ' + str(5 - self.MAX_REPEAT_TIMES + 1))
                self.MAX_REPEAT_TIMES = self.MAX_REPEAT_TIMES - 1
                if self.MAX_REPEAT_TIMES > 0:
                    return self.GetQuote_from_Yahoo(start, end, callback)
                else:
                    self.MAX_REPEAT_TIMES = 5
                    return None, None
        pass

    #取得買賣日報表(交易所)
    def GetExchangeDaily(self, callback = None):
        req = requests.session()
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
        }
        res = req.get(self.EXCHANGE_DAILY_URL + '/bsMenu.aspx', headers = headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'lxml')
        payload = {}
        
        for item in soup.select('input[type=hidden]'):
            if item.get('value'):
                payload[item.get('name')] = item.get('value')
        
        payload['TextBox_Stkno'] = self.stock_no
        payload['__EVENTTARGET'] =''
        payload['__EVENTARGUMENT'] =''
        payload['__LASTFOCUS'] =''
        payload['RadioButton_Normal'] ='RadioButton_Normal'
        payload['btnOK'] = '查詢'   

        res = req.post(self.EXCHANGE_DAILY_URL + '/bsMenu.aspx', data = payload, headers = headers) 
        res = req.get(self.EXCHANGE_DAILY_URL + 'bsContent.aspx', headers = headers)        
        content = res.text        
        self.log.debug(content)
        buf = io.StringIO(content)
        

        
        i = 0
        rs = []
        while True:
            s = buf.readline()            
            if s is not None and s != "":
                if i > 2:
                    #序號,券商,價格,買進股數,賣出股數,,序號,券商,價格,買進股數,賣出股數
                    m = {}
                    strs = s.split(",")
                    if strs[0] != "":
                        m["sn"] = strs[0]
                        m["brokerId"] = strs[1]
                        m["price"] = strs[2]
                        m["buy_volumn"] = strs[3]
                        m["sell_volumn"] = strs[4]
                        rs.append(m)
                    
                    if strs[6] != "":
                        m = {}
                        m["sn"] = strs[6]
                        m["brokerId"] = strs[7]
                        m["price"] = strs[8]
                        m["buy_volumn"] = strs[9]
                        m["sell_volumn"] = strs[10]
            else:
                break
            i = i+1
        if callback is not None:
            callback(rs)
        else:
            return rs

    


    def GetExangeDailyFromWantgoo(self, d, cb = None):
        p = Profiler()
        self.log.info(p.startLog("date: {}", d))
        if d is None:
            d = datetime.datetime.now().strftime("%Y-%m-%d")
        url = "https://www.wantgoo.com/stock/astock/agentstat_ajax?StockNo={id}&Types=3.5&StartDate={ds}&EndDate={de}&Rows=35"
        url = url.format(id=self.stock_no, ds = d, de = d)
        self.log.debug("get wantgoo daily exchange url: " + url)
        resp = requests.get(url)
        dailyReport = resp.json()
        code = dailyReport["code"]
        message = dailyReport["message"]
        returnValues = json.loads(dailyReport["returnValues"])
        if cb is not None:
            cb(returnValues)
        else:
            return returnValues
       


            
            
            
        



        