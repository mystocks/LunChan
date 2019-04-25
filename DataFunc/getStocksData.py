# -*- coding:utf-8 -*-
import os
import sys
rootPath = os.path.dirname(os.getcwd())
sys.path.append(rootPath)
import time
from sqlalchemy import create_engine
import tushare as ts
import pymysql as MySQLdb
import numpy as np
import pandas as pd
from pandas import DataFrame as DF
from quotation.realQuotation import realQuotation
from quotation.realKDayData import realKDayData

#追加数据到现有表
#df.to_sql('tick_data',engine,if_exists='append')
class GetStocksAllData(object):
    all_stock_Id = []
    mRealQuotation = realQuotation()
    mRealKDay = realKDayData()

    def __init__(self):
        self.mRealQuotation.start_work((3,))
        self.mRealKDay.start_work((3,))

    def getRealTimeData_from_Network(self, stockId):
        try:
            df = ts.get_realtime_quotes(stockId)
            re=df[0:1]
        except:
            print("try to get RealTime Data Filed:",stockId)
            return None
        return re


    def getRealQuotationData(self, stocksId):
        return self.mRealQuotation.getQuotation(stocksId)

    def getDataByReqFiled(self, good_id, req_fields):
        # print(good_id, type(good_id))
        result = self.getRealQuotationData(good_id)

        data = []
        c = result.index[0]
        for fid in req_fields:
            rFid = fid
            try:
                ret = result[rFid][c]
            except:
                ret = None
            if ret != None:
                data.append(ret)
            else:
                data.append(0)
        #print(data)
        return data
    def int2StrStockId(self, stockId):
        strId = "%s" % stockId
        if len(strId) < 6:
            left = 6 - len(strId)
            str = ""
            while left > 0:
                str += "0"
                left -= 1
            strId = str + strId
        return strId

    def getKlineData(self, stockId, size, begin, end):
        if type(stockId) == type(123):
            stockId = self.int2StrStockId(stockId)
        ret=self.mRealKDay.get_one_data_form_databases(stockId)
        if ret is None:
            return ret
        count = len(ret)
        if count <= size:
            return ret
        else:
            retSize = 0 - size
            return ret[retSize:]
        pass

    def __del__(self):
        print("Enter getStosksData __del__")
        self.mRealQuotation.stop_work()
        self.mRealKDay.stop_work()
        print("Leaver del")

getStocksData = GetStocksAllData()
retData = getStocksData.getKlineData('603999', 20, 0,0)
print(retData, type(retData))
#getStocksData.getRealQuotationData('603999')
