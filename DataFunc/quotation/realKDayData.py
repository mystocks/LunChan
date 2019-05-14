#coding=utf-8
import os
import sys
rootPath = os.path.dirname(os.getcwd())
sys.path.append(rootPath)
from common.threadingBase import threadingBase #不这么引用不识别class类型
import time
from sqlalchemy import create_engine
import tushare as ts
import pymysql as MySQLdb
import numpy as np
import pandas as pd
from pandas import DataFrame as DF
import datetime
import traceback
import logging
logPath = os.path.join(rootPath, 'mylog.log')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s %(funcName)s [line:%(lineno)d] %(levelname)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S', filename=logPath, filemode='w')
class realKDayData(threadingBase):
    tableNameOfStockId = "AllStockId"
    mConnectDb = None
    mCur = None
    pro = None
    base_ids = None # 存放基础股票ID列表
    def __init__(self):
        super(realKDayData, self).__init__()
        self.bInited = False
        ts.set_token('7877a44c4642265141b606ce604c275fe3dbde782af6739f8eb65760')
        self.pro = ts.pro_api()
        self.mConnectDb = MySQLdb.connect(host='127.0.0.1', user='root', passwd='Root@123')
        if self.mConnectDb != None:
            self.mCur = self.mConnectDb.cursor()
            self.mConnectDb.select_db('stocksdb')
            print("connected to MySQLDb!")

    def get_one_stock_data_toDb_byEngine(self, stockId):
        '''
        存储股票数据到数据库，通过pandas的特殊方法
        '''
        try:
            df = ts.get_k_data(stockId)
            #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://.....'
            engine = create_engine('mysql+pymysql://root:Root@123@127.0.0.1/stocksdb?charset=utf8')
            # 存入数据库
            df.to_sql(stockId+'_KDay', engine, if_exists='replace')
        except:
            logging.error('one stock toDb:\n%s' % traceback.format_exc())
            pass

    def get_all_stock_data_toDb_byEngine(self):
        '''
        获取单只股票近3年日线数据
        '''
        isOk=False
        index=3
        print("Enter get_all_stock_data_toDb_byEngine")
        self.get_all_stock_id_from_network()
        for stockId in self.all_stock_Id:
            print("start to get data ",stockId)
            index=3
            while(index>0):
                try:
                    self.get_one_stock_data_toDb_byEngine(stockId)
                    index=0
                except:
                    index -= 1
                time.sleep(0.5)
        print("Leaver get_all_stock_data_toDb_byEngine")

    def getpro_idname(self, stock_id):
        if self.base_ids is None:
            self.base_ids = self.pro.query('stock_basic', exchange_id='', is_hs='', fields='ts_code,symbol,name,list_date,list_status')
        if self.base_ids is None:
            return None
        onedata = self.base_ids[self.base_ids.symbol == stock_id].values
        return onedata[0][0]

    def change_date_format(self, input_date, add_or_remove = False):
        index = 0
        str_len = len(input_date)
        ret_str = ''
        for i in range(str_len):
            if add_or_remove == True and '-' != input_date[i]:
                ret_str += input_date[i]
            if add_or_remove == False:
                ret_str += input_date[i]
                index += 1
                if index == 4 or index == 6:
                    ret_str += '-'
        return ret_str

    def update_one_stock_toDb_bySql(self, stockId):
        '''
        更新日线数据到数据库
        '''
        logging.info("****Start update id= %s", stockId)
        if False == self.check_Exist_StockTable_InDB(stockId):
            logging.warning("Not exist table:%s_KDay"%stockId)
            self.get_one_stock_data_toDb_byEngine(stockId)
            return False
        ret, retvalues = self.check_stocktable_empty(stockId)
        if False == ret or retvalues is None:
            logging.warning("the table is empty!")
            return
        indexId = retvalues[-1][0]
        startdate = retvalues[-1][1]
        startdate = self.change_date_format(startdate, True)
        enddate = datetime.datetime.now().strftime('%Y%m%d')#现在
        tsname = self.getpro_idname(stockId)
        df = self.pro.daily(ts_code=tsname, start_date=startdate, end_date=enddate) # startdate==enddate时获取当天一组数据
        count=len(df)
        if count <=0:
            logging.warning("no data from ts")
            return False
        valueList = []
        df = np.array(df) # 转换成list
        df_list = df[::-1] # 逆序
        df_list = df_list[1::] #去掉第一个相同的数据
        for oneData in df_list:
            indexId += 1
            valueList.append((indexId,self.change_date_format(oneData[1]),float(oneData[2]),float(oneData[5]),float(oneData[3]),float(oneData[4]),float(oneData[9]),stockId, 99999.9))
        if len(valueList) > 0:
            #sqlline="insert into %s_KDay(date,open,close,high,low,volume,code) values(%%s,%%s,%%s,%%s,%%s,%%s,%%s);"%(stockId)
            sqlline = "insert into %s_KDay values(%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s);" % (stockId)
            logging.info("%s", sqlline)
            try:
                pass
                self.mCur.executemany(sqlline,valueList)
                self.mConnectDb.commit()
            except:
                self.mConnectDb.rollback()
                logging.warning('get_one_data_form_databases:\n%s' % traceback.format_exc())
                return False
        else:
            logging.warning("    Done,no data need to insert id=%s",stockId)
            pass
        return True

    def get_all_stock_id_from_database(self):
        '''
        从数据库读取所有股票代码
        '''
        self.all_stock_Id = []
        try:
            sqlcmd="SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='%s';"%self.tableNameOfStockId
            count = self.mCur.execute(sqlcmd)
            if count == 0:
                print("Error:Not found table =",self.tableNameOfStockId)
                return
        except:
            print("except..")
        cmdline="select stockId from %s"%self.tableNameOfStockId
        count=self.mCur.execute(cmdline)
        if count == 0:
            print("Error:no data in table=",self.tableNameOfStockId)
        self.all_stock_Id=self.mCur.fetchall()
        print("Suc:get stocksId, the total number is ",len(self.all_stock_Id))
        return self.all_stock_Id

    def store_stock_id_to_db_BySql(self):
        '''
        存储所有股票id到数据库
        :return:
        '''
        stockIdList = self.__get_all_stock_id_from_network()
        r1=None
        try:
            sqlcmd="SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='%s';"%self.tableNameOfStockId
            count = self.mCur.execute(sqlcmd)
            if count == 0:
                cmdline="create table %s(id int,stockId varchar(10))"%self.tableNameOfStockId
                print(cmdline)
                self.mCur.execute(cmdline)
            else:
                print("Exist..")
                #return

            valuses=[]
            i=1
            print(len(self.all_stock_Id))
            for id in self.all_stock_Id:
                valuses.append((i,id))
                i=i+1

            print("valuse len=%d"%len(valuses))
            #这里的%需要使用%%转义字符来格式化
            #在sql里无论是什么类型，都使用%s来作为占位符
            cmdline="insert into %s values(%%s,%%s)"%self.tableNameOfStockId
            print(cmdline,valuses[0])
            r1=self.mCur.executemany(cmdline, valuses)
            print(r1)
            self.mConnectDb.commit()
        except:
            print("except...",r1)
            self.mConnectDb.rollback()

    def set_table_date_unique(self):
        '''
        设置表项属性的唯一属性
        '''
        try:
            for stockId in self.all_stock_Id:
                pass
                sqlcmd = "ALTER TABLE '%s_KDay' ADD unique('date');"%stockId
                print(sqlcmd)
                self.mCur.execute(sqlcmd)
                self.mConnectDb.commit()
        except:
            print("ERROR:ADD unique failed")
            self.mConnectDb.rollback()


    def get_one_data_AndCheck_from_databases(self, stockId, subCount):
        '''
        遍历单个股票数据并过滤目标股票ID保存
        '''
        sqlcmd="SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='%s_KDay';"%stockId
        count = self.mCur.execute(sqlcmd)
        if count == 0:
            print("Not exist table:%s_KDay"%stockId)
            return False
        sqlcmd = "select * from %s_KDay"%stockId
        #param = stockId+"_KDay"
        count=self.mCur.execute(sqlcmd)
        if count <=90:
            return False
        offset = count - 90
        count = 15-3
        self.mCur.scroll(offset, mode='absolute')
        results = self.mCur.fetchall()
        for i in range(count):
            row = i+75
            increaseRate=0.01
            open1=results[row][2]
            open2=results[row+1][2]
            open3=results[row+2][2]
            close1=results[row][3]
            close2 = results[row+1][3]
            close3 = results[row+2][3]
            vol1 = results[row][6]
            vol2 = results[row+1][6]
            vol3 = results[row+2][6]
            #print results[row][2], results[row][3],results[row+1][2], results[row+1][3], results[row+2][2], results[row+2][3]
            if close2 > (close1+close1*increaseRate) and  close3 > (close2+close2*increaseRate):
                if vol2 > (vol1+vol1*increaseRate) and  vol3 > (vol2+vol2*increaseRate):
                    for j in range(subCount):
                        closex=results[row-j][3]
                        if close3 < closex:
                            return False
                    #print stockId,results[row][1],close1
                    return True

    def get_All_data_from_databases_AndCheck(self, functionName, subcount):
        '''
        遍历所有股票数据并过滤目标股票ID保存
        '''
        self.get_all_stock_id_from_database()
        rList=[]
        curCount=0
        allCount=len(self.all_stock_Id)
        for stockId in self.all_stock_Id:
            if True == self.get_one_data_AndCheck_from_databases(stockId, subcount):
                rList.append(stockId)
            if functionName != None:
                functionName(curCount, allCount)
            curCount+=1
        return rList

    def get_all_stock_id_from_network(self):
    # 获取所有股票代码
        self.all_stock_Id = []
        try:
            stock_info=ts.get_stock_basics()
            for i in stock_info.index:
                self.all_stock_Id.append(i)
            #print(len(self.all_stock_Id))
        except:
            print('result is:\n%s' % traceback.format_exc())

    def get_all_stockId(self):
        filePathName = os.path.join(rootPath, "data", "AllStockId.csv")
        if os.path.exists(filePathName):
            ret = pd.read_csv(filePathName, encoding='utf8')
            idsArr = np.array(ret['stockIds'])
            ids = idsArr.tolist()
            return ids
        else:
            self.get_all_stock_id_from_network()
            if len(self.all_stock_Id) != 0:
                c = {"stockIds": self.all_stock_Id}
                data = DF(c)
                data.to_csv(filePathName, encoding='utf8')
                return self.all_stock_Id

    def update_all_data_to_db_bySql(self, functionName=None):
        '''
        更新所有日线数据到数据库
        :return:
        '''
        curCount=1
        allCount=0
        #self.get_all_stock_id_from_database()
        retIds = self.get_all_stockId()
        logging.info("the input Id is %s", retIds)
        #allCount=len(self.all_stock_Id)
        for item in retIds:
            # 这里的stockId是一个tuple
            stockId = "%s"%item
            if len(stockId) < 6:
                left = 6-len(stockId)
                str = ""
                while left > 0:
                    str += "0"
                    left -= 1
                stockId = str + stockId
            try:
                ret = self.update_one_stock_toDb_bySql(stockId)
                if ret == True:
                    curCount += 1
            except:
                logging.info('updata KDay Data Failed:\n%s' % traceback.format_exc())
            if functionName != None:
                functionName(curCount, allCount)
            logging.info("update suc count = %d", curCount)
            time.sleep(5)

    def check_Exist_StockTable_InDB(self,stockId):
        '''
        判断对应股票表是否存在于数据库中
        :param stockId:
        :return True or False:
        '''
        sqlcmd="SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='%s_KDay';"%stockId
        count = self.mCur.execute(sqlcmd)
        if count == 0:
            logging.warning("Not exist table:%s_KDay"%stockId)
            return False
        return True

    def check_stocktable_empty(self, stockid):
        sqlline = "select * from %s_KDay;" % (stockid)
        datacount = self.mCur.execute(sqlline)
        if datacount == 0:
            logging.warning("table is empty")
            return False,None
        retList = self.mCur.fetchall()
        return True, retList

    def __del__(self):
        super(realKDayData, self).__del__()
        self.mConnectDb.close()
        self.mCur.close()

    def work_func(self, args):
        self.bExitWorkFunc = False  # 线程开始执行未退出
        while self.bStop == False: # loop 1
            curtime = datetime.datetime.now()
            if (curtime.hour+8) == 24:
                logging.info(curtime)
                logging.info("start to update kdata")
                self.update_all_data_to_db_bySql()
                pass
                time.sleep(7200)
            logging.info("wait start to update,%s", curtime.strftime("%Y-%m-%d-%H"))
            time.sleep(120)

        self.bExitWorkFunc = True # 线程执行完毕
        # end func

    def get_one_data_form_databases(self, stockId):
        '''
        从数据库读取所有股票信息，并返回结果List
        :param stockId:
        :return:
        '''
        if False == self.check_Exist_StockTable_InDB(stockId):
            return None
            #self.get_one_stock_data_toDb_byEngine(stockId)

        retList=[]
        try:
            cmdline="select date,open,close,high,low,volume,predict1 from %s_KDay;"%stockId
            logging.info('cmdline = %s', cmdline)
            count=self.mCur.execute(cmdline)
            if count == 0:
                return None
            retList=self.mCur.fetchall()
        except:
            logging.warning('get_one_data_form_databases:\n%s' % traceback.format_exc())
        if len(retList) >0:
            return retList
        return None



myKDay = realKDayData()
id = '603999'
#tscode = myKDay.getpro_idname(id)
#print(tscode, type(tscode))
#myKDay.update_one_stock_toDb_bySql(id)
#ret = myKDay.get_all_stock_data_toDb_byEngine()
#ret = myKDay.get_one_data_form_databases('603999')
#print(ret)
#print(type(ret))
#myKDay.get_one_stock_data_toDb_byEngine(id)