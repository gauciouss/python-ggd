from sqlalchemy import Column, String, INT, Float, Date, DateTime, BIGINT
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging

base = declarative_base()

#Yahoo盤後報價
class TWStockQuote(base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'tw_stock_quote'
    stk_id = Column(String(20), primary_key = True)
    q_date = Column(Date, primary_key = True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volumn = Column(BIGINT) #成交股數    
    updown = Column(INT)    #漲跌
    updown_limit = Column(Float)    #漲跌幅    
    ewma = Column(Float)
    A = Column(Float)


#TWSE盤後報價
class TWSEStkQuote(base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'TWSE_STK_QUOTE'
    STK_ID = Column(String(10), primary_key = True)
    Q_DATE = Column(Date, primary_key = True)       
    VOLUMN = Column(BIGINT) #成交股數
    TOTAL_PRICE = Column(Float) #成交金額
    OPEN = Column(Float)
    HIGH = Column(Float)
    LOW = Column(Float)
    CLOSE = Column(Float)
    P_DISTANCE = Column(Float) #漲跌價差
    TOTAL_COUNT = Column(BIGINT) #成交筆數
    
#證券商品
class StockList(base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'TW_STOCK_LIST'
    STOCK_ID = Column(String(20), primary_key = True)
    COMP_NAME = Column(String(50))
    STOCK_NAME = Column(String(10))
    FOREIGN_COUNTRY_REGISTERED = Column(String(100))
    INDUSTRY = Column(INT)
    ADDRESS = Column(String(100))
    TAX_ID_NUMBER = Column(String(8))
    CHAIRMAN = Column(String(50))
    GENERAL_MANAGER = Column(String(50))
    SPOKES_MAN = Column(String(50))
    ESTABLISHMENT_DATE = Column(Date)
    LIST_DATE = Column(Date)
    CAPITAL_AMOUNT = Column(BIGINT)
    PRIVATE_EQUITY = Column(BIGINT)
    PREFERED_EQUITY = Column(BIGINT)

    

#TWSE買賣日報表
class TwStkBuySellDaily(base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'TW_STK_BUY_SELL_DAILY'
    STK_ID = Column(String(10), primary_key = True)
    V_DATE = Column(Date, primary_key = True)
    PRC_BUY_VOLUMN = Column(BIGINT)
    PRC_SELL_VOLUMN = Column(BIGINT)
    PRC_OVER_BUY_SELL_VOLUMN = Column(BIGINT)
    FORRIGN_SELF_EMPLOYED_BUY_VOLUMN = Column(BIGINT)
    FOREIGN_SELF_EMPLOYED_SELL_VOLUMN = Column(BIGINT)
    FOREIGN_SELF_EMPLOYED_OVER_BUY_SELL_VOLUMN = Column(BIGINT)
    SITCA_BUY_VOLUMN = Column(BIGINT)
    SITCA_SELL_VOLUMN = Column(BIGINT)
    SITCA_OVER_BUY_SELL_VOLUMN = Column(BIGINT)
    SELF_EMPLOYED_OVER_BUY_SELL_VOLUMN = Column(BIGINT)
    SELF_EMPLOYED_BUY_VOLUMN_SELF = Column(BIGINT)
    SELF_EMPLOYED_SELL_VOLUMN_SELF = Column(BIGINT)
    SELF_EMPLOYED_OVER_BUY_SELL_SELF = Column(BIGINT)    
    SELF_EMPLOYED_BUY_VOLUMN_RISK = Column(BIGINT)
    SELF_EMPLOYED_SELL_VOLUMN_RISK = Column(BIGINT)
    SELF_EMPLOYED_OVER_BUY_SELL_RISK = Column(BIGINT)
    TOTAL_OVER_BUY_SELL_VOLUMN = Column(BIGINT)

class ExchangeDailyReport(base):
    __table_args__ = {"extend_existing": True}
    __tablename__ = "exchange_daily_report"
    stk_id = Column(String(10), primary_key = True)
    brokerId = Column(String(10), primary_key = True)
    date = Column(Date, primary_key = True)
    price = Column(Float)
    buy_volumn = Column(BIGINT)
    sell_volumn = Column(BIGINT)