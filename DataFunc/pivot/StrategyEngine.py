# -- coding: utf-8 --
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pandas as pd
from pandas import np
from pandas import DataFrame as df
import talib

class StrategyEngine(object):
    def __init__(self):
        pass

    def getDayPivot(self, dayCloseList):
        '''
        获取日线中枢
        :param dayCloseList:
        :return:
        '''
        retList=[]
        len = len(dayCloseList)
        if len <= 3:
            return None
        nrCloses=np.array(dayCloseList)
        sma3 = talib.SMA(nrCloses, timeperiod=3)
        '''
        
        '''
        len3=len(sma3)
        for i in range(3,len3):
            first=sma3[i]
            second=sma3[i+1]
            if