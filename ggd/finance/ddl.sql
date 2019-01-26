#證券商品報價
create table TW_STK_QUOTE (
    STK_ID      VARCHAR(10),
    Q_DATE      DATE,
    OPEN        FLOAT,
    HIGH        FLOAT,
    LOW         FLOAT,
    CLOSE       FLOAT,
    ADJ_CLOSE   FLOAT,
    VOLUMN      BIGINT,
    TOTAL_COUNT BIGINT,
    CONSTRAINT PRIMARY KEY(STK_ID, Q_DATE)
);

#每日買賣日報表
create table TW_STK_BUY_SELL_DAILY (
    STK_ID                                      VARCHAR(10),
    V_DATE                                      DATE,
    PRC_BUY_VOLUMN                              BIGINT,
    PRC_SELL_VOLUMN                             BIGINT,
    PRC_OVER_BUY_SELL_VOLUMN                    BIGINT,
    FORRIGN_SELF_EMPLOYED_BUY_VOLUMN            BIGINT,     #外資自營商買入股數
    FOREIGN_SELF_EMPLOYED_SELL_VOLUMN           BIGINT,     #外資自營商賣出股數
    FOREIGN_SELF_EMPLOYED_OVER_BUY_SELL_VOLUMN  BIGINT,     #外資自營商買賣超股數
    SITCA_BUY_VOLUMN                            BIGINT,     #投信買進股數
    SITCA_SELL_VOLUMN                           BIGINT,     #投信賣出股數
    SITCA_OVER_BUY_SELL_VOLUMN                  BIGINT,     #投信買賣超股數
    SELF_EMPLOYED_OVER_BUY_SELL_VOLUMN          BIGINT,     #自營商買賣超股數
    SELF_EMPLOYED_BUY_VOLUMN_SELF               BIGINT,     #自營商買入股數(自行買賣)
    SELF_EMPLOYED_SELL_VOLUMN_SELF              BIGINT,     #自營商賣出股數(自行買賣)
    SELF_EMPLOYED_OVER_BUY_SELL_SELF            BIGINT,     #自營商買賣超股數(自行買賣)
    SELF_EMPLOYED_BUY_VOLUMN_RISK               BIGINT,     #自營商買入股數(避險)
    SELF_EMPLOYED_SELL_VOLUMN_RISK              BIGINT,     #自營商賣出股數(避險)
    SELF_EMPLOYED_OVER_BUY_SELL_RISK            BIGINT,     #自營商買賣超股數(避險)
    TOTAL_OVER_BUY_SELL_VOLUMN                  BIGINT,     #三大法人買賣超股數
    CONSTRAINT PRIMARY KEY(STK_ID, V_DATE)
);

create table TW_STOCK_INDUSTRY(
    SERIAL_NO INT AUTO_INCREMENT,
    NAME VARCHAR(10),
    CONSTRAINT PRIMARY KEY(SERIAL_NO)
);

insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (1, '水泥工業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (2, '食品工業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (3, '其他');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (4, '塑膠工業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (5, '化學工業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (6, '汽車工業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (7, '紡織纖維');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (8, '貿易百貨');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (9, '建材營造');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (10, '電子零組件業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (11, '電機機械');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (12, '生技醫療業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (13, '電器電纜');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (14, '玻璃陶瓷');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (15, '造紙工業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (16, '鋼鐵工業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (17, '橡膠工業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (18, '航運業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (19, '電腦及週邊設備業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (20, '半導體業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (21, '其他電子業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (22, '通信網路業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (23, '光電業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (24, '電子通路業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (25, '資訊服務業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (26, '油電燃氣業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (27, '觀光事業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (28, '金融保險業');
insert into TW_STOCK_INDUSTRY(SERIAL_NO, NAME) values (29, '存託憑證');



create table TW_STOCK_LIST (
    STOCK_ID    VARCHAR(20),                    #股票代碼
    COMP_NAME   VARCHAR(50),                    #公司名稱
    STOCK_NAME  VARCHAR(10),                    #股票名稱
    FOREIGN_COUNTRY_REGISTERED  VARCHAR(100),   #外國企業註冊地國
    INDUSTRY    INT,                            #產業別
    ADDRESS     VARCHAR(100),                    #住址
    TAX_ID_NUMBER   VARCHAR(8),                 #統一編號
    CHAIRMAN        VARCHAR(50),                #董事長
    GENERAL_MANAGER VARCHAR(50),                #總經理
    SPOKES_MAN      VARCHAR(50),                #發言人
    ESTABLISHMENT_DATE   DATE,                  #成立日期
    LIST_DATE       DATE,                       #上市日期
    CAPITAL_AMOUNT  BIGINT,                       #實收資本額
    PRIVATE_EQUITY  BIGINT,                       #私募股數
    PREFERED_EQUITY  BIGINT,                      #特別股
    CONSTRAINT PRIMARY KEY(STOCK_NO)
);