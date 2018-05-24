# -*- coding=utf-8 -*-
import os
import sys
#python默认就是utf8
rootPath = os.path.dirname(os.getcwd())
sys.path.append(rootPath)
from common.threadingBase import threadingBase #不这么引用不识别class类型
import time
import tushare as ts
import pandas as pd
import json

class realQuotation(threadingBase):
    def __init__(self):
        super(realQuotation, self).__init__()
        print ("Enter realQuotation.")
        self.bIsGetTodayData = False # 表示是否获取数据
        self.realData = None

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
            re=df[0:1]
        except:
            print(("try to get RealTime Data Filed:",stockId))
            return None
        return re

    def work_func(self, args):
        while self.bStop == False:
            if self.checkIfExistRealDataFile() == False:
                self.bIsGetTodayData = False
            else:
                self.bIsGetTodayData = True

            if self.bIsGetTodayData == False:
                try:
                    re = ts.get_today_all()
                    self.realData = re
                    self.writedata_tocsv(re)
                    self.bIsGetTodayData = True
                except :
                    self.bIsGetTodayData == False
                    print("ERROR:get_today_all:")

                if self.bIsGetTodayData == False:
                    time.sleep(3)
                    continue
            else:
                self.realData = self.readdata_fromcsv()
                #stockId = '603999'
                #r1 = self.getRealTimeData_from_Network(stockId)

            if self.bIsGetTodayData == True:
                time.sleep(6)
            else:
                time.sleep(3)

        self.bExitWorkFunc = True # 线程执行完毕
        # end func

    def getQuotation(self, id):
        '''
        获取单只股票的实时行情
        :param id:股票代码字符串
        :return:
        '''
        if id == None or len(id) == 0 or len(id) > 6:
            return None
        #由于返回的DF中的code是int型，所以这里需要转换后才能比较
        iId = int(id)
        if self.bIsGetTodayData:
            print ("get data From base")
            return self.realData[self.realData.code == iId]
        else:
            print ("get data from NetWork")
            return self.getRealTimeData_from_Network(id)

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