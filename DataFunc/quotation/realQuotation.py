# -*- coding=utf-8 -*-
import os
import sys
import numpy as np

#python默认就是utf8
rootPath = os.path.dirname(os.getcwd())
sys.path.append(rootPath)
from common.threadingBase import threadingBase #不这么引用不识别class类型
import time
import tushare as ts
import pandas as pd
import json
import traceback

class realQuotation(threadingBase):
    def __init__(self):
        super(realQuotation, self).__init__()
        print ("Enter realQuotation.")
        self.bIsGetTodayData = False # 表示是否获取数据
        self.realData = None
        self.requestIds = [] #已请求的stockid列表
        ts.set_token('7877a44c4642265141b606ce604c275fe3dbde782af6739f8eb65760')
        self.pro = ts.pro_api()

    def __del__(self):
        super(realQuotation, self).__del__()
        self.realData = None

    def getFilePathName(self):
        tTime = time.localtime()
        tDay = tTime.tm_mday
        if tTime.tm_hour < 18:
            tDay = tDay - 1
        #upData = time.strftime("%Y-%m-%d", tTime.tm_year, tTime.tm_mon, tDay)
        upData = "%04d-%02d-%02d" % (tTime.tm_year, tTime.tm_mon, tDay)
        upFileName = "RealTimeData-" + upData + ".csv"
        filePathName = os.path.join(rootPath, "data", upFileName)
        #print(("dataPath:", filePathName))
        return filePathName

    def checkIfExistRealDataFile(self):
        filePath = self.getFilePathName()
        if os.path.exists(filePath):
            return True
        return False

    def writedata_tocsv(self, allData):
        '''
        把所有股票实时数据写入文件中
        :param allData:
        :return:
        '''
        dataPath = self.getFilePathName()
        allData.to_csv(dataPath, encoding='utf8')
        return True

    def readdata_fromcsv(self):
        dataPath = self.getFilePathName()
        updata = pd.read_csv(dataPath, encoding='utf8')
        return updata

    def getRealTimeData_from_Network(self, stockId):
        try:
            df = ts.get_realtime_quotes(stockId)
            if df is None:
                print("get_realtime_quotes: stockId = ", stockId)
                return None
            # 获取的数据元素是str类型，需要转换成float或者int64
            dfColmuns = ['open', 'pre_close', 'price', 'high', 'low', 'bid', 'ask',
                         'volume', 'amount']
            # 个别股票这里是空，直接调用astype会导致异常
                #, 'b1_v', 'b1_p', 'b2_v', 'b2_p', 'b3_v', 'b3_p',
                #'b4_v', 'b4_p', 'b5_v', 'b5_p', 'a1_v', 'a1_p', 'a2_v', 'a2_p', 'a3_v',
                #        'a3_p', 'a4_v', 'a4_p', 'a5_v', 'a5_p'
            df['code'] = df['code'].astype('int64')
            df[dfColmuns] = df[dfColmuns].astype('float64')
            re=df[0:1]
        except:
            print('getRealTimeData_from_Network:\n%s' % traceback.format_exc())
            return None
        return re

    def work_func(self, args):
        self.bExitWorkFunc = False  # 线程开始执行未退出
        loopCount = 0
        while self.bStop == False: # loop 1
            if loopCount % 3 == 0:
                self.bIsGetTodayData = self.updateAllTodayDataAtSix()
            self.updateRequestIdData()
            time.sleep(6)

        self.bExitWorkFunc = True # 线程执行完毕
        # end func

    def addNewRequestId(self, newId):
        '''
        缓存已请求的股票Id，定时刷新
        :param idList:
        :return:
        '''
        if newId not in self.requestIds:
            self.requestIds.append(newId)
        return

    def getQuotation(self, id):
        '''
        获取单只股票的实时行情
        :param id:股票代码字符串
        :return:
        '''
        if id == None or len(id) == 0 or len(id) > 6:
            return None
        #由于返回的DF中的code是int型，所以这里需要转换后才能比较
        if id in ['sh', 'sz', 'cyb']:
            t = self.getRealTimeData_from_Network(id)
            if t is None:
                return None
            pre_close = (float)(t['pre_close'][0])
            price = (float)(t['price'][0])
            #print(pre_close, price, type(pre_close), type(price))
            change = (float)(price - pre_close)/pre_close
            t['price'][0] = price
            #print(type(t['price'][0]))
            t['changepercent'] = 0.0
            t['changepercent'][0] = change* 100.0
            t['zhangdie'] = 0.0
            t['zhangdie'][0] = price - pre_close
            return t
        self.addNewRequestId(id) #先缓存用于更新
        if self.bIsGetTodayData:
            #print ("get data From base")
            iId = int(id)
            ret = self.realData[self.realData.code == iId]
            if len(ret) == 0:
                iId = int(id)
                ret = self.realData[self.realData.code == iId]
            return ret
        else:
            #print ("get data from NetWork")
            return self.getRealTimeData_from_Network(id)


    def add_other_columns(self, dfData):
        '''
        在总表的基础上增加其他列，通过个股实时行情填充
        :param dfData:
        :return:
        '''
        if dfData is None:
            return
        labels = ['zhangdie', 'bid', 'ask', 'b1_v', 'b1_p', 'b2_v', 'b2_p', 'b3_v', 'b3_p',
                  'b4_v', 'b4_p', 'b5_v', 'b5_p', 'a1_v', 'a1_p', 'a2_v', 'a2_p', 'a3_v','a3_p', 'a4_v', 'a4_p',
                  'a5_v', 'a5_p', 'date', 'time']
        dfData.rename(columns={'trade':'price', 'settlement':'pre_close'}, inplace = True)
        columns = dfData.columns.values.tolist()
        for item in labels:
            if item not in columns:
                # 新增的列全部赋值为浮点数0.0
                dfData[item] = 0.0
        # date/time需要字符串类型
        dfData[[ 'date', 'time']] = dfData[[ 'date', 'time']].astype('str')
        dfData['code'] = dfData['code'].astype('int64')

    def getTodayAllData(self):
        tTime = time.localtime()
        tDay = tTime.tm_mday
        if tTime.tm_hour < 18:
            tDay = tDay - 1

        todayDate = "%04d%02d%02d" % (tTime.tm_year, tTime.tm_mon, tDay)
        print(todayDate)
        re = self.pro.daily_basic(ts_code='', trade_date=todayDate)
        print(re)
        return re

    def updateAllTodayDataAtSix(self):
        '''
        一次性更新全天数据
        :return:
        False:失败
        True:成功
        '''
        bRet = False
        if self.checkIfExistRealDataFile() == False:  # 检测今日数据文件是否存在
            try:
                #re = ts.get_today_all()
                re = self.getTodayAllData()
                self.add_other_columns(re)
                re['zhangdie'] = re['changepercent'] * 0.01 * re['pre_close']
                self.realData = re
                self.writedata_tocsv(re)
                bRet = True
            except:
                print('get_today_all:\n%s' % traceback.format_exc())
                bRet == False
                print("ERROR:get_today_all:")
        else:
            if self.bIsGetTodayData == False:
                self.realData = self.readdata_fromcsv()
            bRet = True
        return bRet

    def updateRequestIdData(self):
        '''
        更新请求过的股票信息
        :return:
        '''
        if self.bIsGetTodayData == False:
            return
        for id in self.requestIds:
            try:
                ret = self.getRealTimeData_from_Network(id)
                if ret is not None:
                    valuesList = np.array(ret[0:1]).tolist()
                    iId = int(id)
                    #print(iId, self.realData[self.realData.code == iId])
                    #print(type(self.realData['code'][0]), type(self.realData['price'][0]))
                    index = self.realData[self.realData.code == iId].index[0]
                    #print(index)
                    # 赋值后变成code变成了字符串
                    self.realData.loc[index, ret.columns.values.tolist()] = valuesList[0]
                    price = (float)(self.realData.loc[index, 'price'])
                    pre_close = (float)(self.realData.loc[index, 'pre_close'])
                    zhangdie = (float)(price) - (float)(pre_close)
                    self.realData.loc[index, 'zhangdie'] = zhangdie
                    self.realData.loc[index, 'changepercent'] = zhangdie*100.0 / pre_close
                    #print(self.realData[self.realData.code == id])
            except:
                print("try to update Failed,id = ", id)
                print('updateRequestIdData:\n%s' % traceback.format_exc())
                continue
#getRealQuotation = realQuotation()
#temp = getRealQuotation.readdata_fromcsv()
#getRealQuotation.start_work((3,))
#time.sleep(5)
#print(type(temp))
#result = temp[0]
#print (temp[temp.code == '603999'])
#print(result.iloc[0, ])
#getRealQuotation.stop_work()
#del getRealQuotation