# -*- coding:utf-8 -*-
import os
import time
from sqlalchemy import create_engine
import tushare as ts
import pymysql as MySQLdb
import numpy as np
import pandas as pd
from pandas import DataFrame as DF

#追加数据到现有表
#df.to_sql('tick_data',engine,if_exists='append')
class GetStocksAllData(object):
    all_stock_Id=[]
    tableNameOfStockId="AllStockId"
    mConnectDb=None
    mCur=None

    def __init__(self):
        self.mConnectDb=MySQLdb.connect(host='127.0.0.1',user='root',passwd='Root@123')
        if self.mConnectDb != None:
            self.mCur=self.mConnectDb.cursor()
            self.mConnectDb.select_db('stocksdb')
            print("connected to MySQLDb!")

    def getPersonalZXGList(self, personalId):
        '''
        get personal zxg stock Ids
        :param personalId:
        :return stockList:
        '''
        return None

    def getRealTimeData_from_Db(self, stockId):
        pass

    def getRealTimeData_from_Network(self, stockId):
        try:
            df = ts.get_realtime_quotes(stockId)
            re=df[0:1]
        except:
            print("try to get RealTime Data Filed:",stockId)
            return None
        return re
        
    def get_all_stock_id_from_network(self):
    # 获取所有股票代码
        self.all_stock_Id = []
        stock_info=ts.get_stock_basics()
        for i in stock_info.index:
            self.all_stock_Id.append(i)
        print(len(self.all_stock_Id))

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

    def __get_one_stock_data_toDb_byEngine(self, stockId):
        '''
        存储股票数据到数据库，通过pandas的特殊方法
        '''
        df = ts.get_k_data(stockId)
        engine = create_engine('mysql://root:Root@123@127.0.0.1/stocksdb?charset=utf8')
        # 存入数据库
        df.to_sql(stockId+'_KDay', engine, if_exists='replace')

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
                    self.__get_one_stock_data_toDb_byEngine(stockId)
                    index=0
                except:
                    index -= 1
                time.sleep(3)
        print("Leaver get_all_stock_data_toDb_byEngine")

    def update_one_stock_toDb_bySql(self, stockId):
        '''
        更新日线数据到数据库
        '''
        sqlcmd="SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='%s_KDay';"%stockId
        count = self.mCur.execute(sqlcmd)
        #print "****Start id=", stockId
        if count == 0:
            print("    Not exist table:%s_KDay"%stockId)
            return
        else:
            sqlline="select * from %s_KDay;"%(stockId)
            dataCount=self.mCur.execute(sqlline)
            if dataCount == 0:
                #print "    table is empty"
                return
        valueList=[]

        df = ts.get_k_data(stockId)
        count=len(df)
        indexId=0
        if count <=2:
            #print "    no data from ts"
            return

        if count > 20:
            indexId = count - 20
            count = 20
            data=df[-20:]
        else:
            data=df
        #print data
        va=data.values

        for index in range(count):
            oneData=va[index]
            curDate=oneData[0]
            sqlline="select * from %s_KDay where date='%s';"%(stockId,curDate)
            dateCount=self.mCur.execute(sqlline)
            if dateCount >=1:
                indexId = indexId + 1
                continue
            valueList.append((indexId,oneData[0],oneData[1],oneData[2],oneData[3],oneData[4],oneData[5],oneData[6]))
            indexId = indexId + 1
        #print valueList
        if len(valueList) > 0:
            #sqlline="insert into %s_KDay(date,open,close,high,low,volume,code) values(%%s,%%s,%%s,%%s,%%s,%%s,%%s);"%(stockId)
            sqlline = "insert into %s_KDay values(%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s);" % (stockId)
            try:
                pass
                self.mCur.executemany(sqlline,valueList)
                self.mConnectDb.commit()
            except:
                self.mConnectDb.rollback()
            #print "    Done id=",stockId
        else:
            #print "    Done,no data need to insert id=",stockId
            pass

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

    def update_all_data_to_db_bySql(self, functionName=None):
        '''
        更新所有日线数据到数据库
        :return:
        '''
        curCount=1
        allCount=0
        self.get_all_stock_id_from_database()
        allCount=len(self.all_stock_Id)
        for stockId in self.all_stock_Id:
            # 这里的stockId是一个tuple
            self.update_one_stock_toDb_bySql(stockId[0])
            if functionName != None:
                functionName(curCount, allCount)
            curCount+=1
            time.sleep(0.1)

    def check_Exist_StockTable_InDB(self,stockId):
        '''
        判断对应股票表是否存在于数据库中
        :param stockId:
        :return True or False:
        '''
        sqlcmd="SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='%s_KDay';"%stockId
        count = self.mCur.execute(sqlcmd)
        if count == 0:
            print("Not exist table:%s_KDay"%stockId)
            return False
        return True

    def get_one_data_form_databases(self, stockId):
        '''
        从数据库读取所有股票信息，并返回结果List
        :param stockId:
        :return:
        '''
        if False == self.check_Exist_StockTable_InDB(stockId):
            return None

        retList=[]
        cmdline="select date,open,close,high,low,volume from %s_KDay;"%stockId
        count=self.mCur.execute(cmdline)
        if count == 0:
            return None
        retList=self.mCur.fetchall()
        if len(retList) >0:
            return retList
        return None

    def __del__(self):
        self.mConnectDb.close()
        self.mCur.close()
        print("Leaver del")


getStocksData = GetStocksAllData()
#获取当前实时数据
result=getStocksData.getRealTimeData_from_Network('603999')
print(type(result))
print(result.columns)
print(result.values)
#name=result.loc[0, 'name']
#print(name)
#print "start"
# 首次更新股票数据到mysql
#getStocksData.get_all_stock_data_toDb_byEngine()

#todaytime = time.strftime('%Y-%m-%d',time.localtime(time.time()))
#getStocksData.store_stock_id_to_mySql()
#getStocksData.get_all_stock_id()
#getStocksData.get_one_data_from_databases('600137')
#getStocksData.get_All_data_from_databases_AndCheck()
#getStocksData.get_one_stock_toDb_bySql('603999')

# 1、更新股票数据到数据库
#getStocksData.update_data_to_db_bySql()

# 2、过滤股票
#getStocksData.get_All_data_from_databases_AndCheck()

# 3、从数据库获取单个股票数据
#retList=getStocksData.get_one_data_form_databases('603999')
#for one in retList:
    #print one
#getStocksData.get_all_stock_id_from_database()
#getStocksData.set_table_date_unique()
#获取所有股票近3年日线数据
#getStocksData.get_all_stock_data_to_db()

#获取单只股票近3年日线数据
#getStocksData.get_one_stock_D_data_to_db('603999')
#del getStocksData