#<span style="font-size:14px;">
# -- coding: utf-8 --  
import requests
import numpy as np     
from matplotlib import pyplot as plt
from matplotlib import dates as dt
from matplotlib import animation
from matplotlib.widgets import Button,RadioButtons
from matplotlib.finance import candlestick_ohlc
from . import getStocksData
import talib
import numpy as np
from PIL import Image
import sys

class CMainBoard(object):

    getData=None
    stocksList=None
    index=1

    def init_data(self):
        self.getData = getStocksData.GetStocksAllData()
        print('更新股票数据：')
        self.getData.update_data_to_db_bySql(self.updateProcessCallback)
        print('过滤股票数据：')
        self.stocksList = self.getData.get_All_data_from_databases_AndCheck(self.updateProcessCallback, 30)
        self.index=1

    def updateProcessCallback(self, cur, all):
        curCount=0.0+cur
        if all <= 0:
            return
        progress= (curCount/all)*100
        outstr='%d%%'%progress
        sys.stdout.write("%.4f" % progress)
        sys.stdout.write("%\r")
        sys.stdout.flush()

    def PlotDemo1(self, fig, stockId):
        #fig  = plt.figure()
        fig.suptitle(stockId, fontsize=14, fontweight='bold')

        retList = self.getData.get_one_data_form_databases(stockId)
        localList=retList[-100:]#获取后100个数据
        dates=[]
        closes=[]
        volumes=[]
        count = []
        dstList=[]
        i=0
        for one in localList:
            dates.append(one[0])
            closes.append(one[2])
            volumes.append(one[5])
            dstList.append((i,one[1], one[4], one[3], one[2],one[5]))
            count.append(i)
            i=i+1

        ax1 = plt.subplot2grid((4,4),(0,0),rowspan=3,colspan=4)

        #ax1.set_title("axes title")
        #ax1.set_xlabel("time1")
        ax1.set_ylabel("Price")
        # 1234是横坐标，否则默认是0开始
        #ax1.plot(count,closes)
        #画出蜡烛图
        print(dstList)
        candlestick_ohlc(ax1, dstList, width=1.2, colorup='r', colordown='g')
        #  画出三日均线图
        nrCloses=np.array(closes)
        sma3 = talib.SMA(nrCloses, timeperiod=3)
        # 画出13日均线图
        ax1.plot(count,sma3)
        sma13 = talib.SMA(nrCloses, timeperiod=13)
        ax1.plot(count,sma13)
        plt.legend(('daily', 'SMA3', 'SMA13'))
        plt.grid(True)
        # 隐藏第一个的X标签
        plt.setp(ax1.get_xticklabels(), visible=False)
        # 调整底部空间大小
        plt.subplots_adjust(bottom=0.1, top=0.95,hspace=0)

        ax2 = plt.subplot2grid((4,4),(3,0),colspan=4)
        ax2.set_xlabel("Time")
        ax2.set_ylabel("Vol")
        #ax2.xaxis.set_major_locator(dt.DayLocator(interval=15))
        for label in ax2.xaxis.get_ticklabels():
            label.set_rotation(45)
        ax2.bar(count,volumes)
        plt.grid(True)
        #plt.show()

#PlotDemo1()



    def on_press(self, event):
        if event.inaxes == None:
            print("none")
            return

        Id=self.stocksList[self.index]
        self.index+=1
        print(Id)
        fig = event.inaxes.figure
        self.PlotDemo1(fig, Id)
        #ax = fig.add_subplot(122)
        #img_gray = Image.open("./Alex.jpg").convert("L")
        #ax.imshow(img_gray, cmap="gray")
        #ax.imshow(img_gray)
        print(event.x,event.xdata, event.ydata)
        #ax1.scatter(event.xdata, event.ydata)
        #plt.axis("off")
        fig.canvas.draw()

    def MainGUI(self):
        fig = plt.figure(figsize=(16, 8))
        index = 0
        fig.canvas.mpl_connect("button_press_event", self.on_press)
        #ax1 = fig.add_subplot(121)
        #ax1.imshow(img)
        #plt.axis("off")
        self.PlotDemo1(fig, self.stocksList[0])
        plt.show()

myBoard=CMainBoard()
myBoard.init_data()
myBoard.MainGUI()