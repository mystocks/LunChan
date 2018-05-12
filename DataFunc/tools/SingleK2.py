# -*- coding:utf-8 -*-
import matplotlib as mpl
import tushare as ts
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
from matplotlib.pylab import date2num
import datetime
import pandas as pd
#%matplotlib inline

df2=pd.DataFrame(pd.np.arange(16).reshape((4,4)),index=['a','b','c','d'],columns=['one','two','three','four'])
print(df2)
list=pd.np.arange(16,30)
list2=list[-10:]
print(list)
print(list2)
