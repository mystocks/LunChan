# -*- coding:utf-8 -*-
import sys
import os
import time,threading

class threadingBase(object):
    def __init__(self):
        self.bStop = False
        self.bExitWorkFunc = True # 表示线程是否已经退出
        self.tHandle = None

    def work_func(self, args):
        while self.bStop == False:
            time.sleep(1)

    def start_work(self, args):
        self.tHandle = threading.Thread(target=self.work_func, args=args)
        self.bStop = False
        self.tHandle.start()

    def stop_work(self):
        print ("Base:stop_work")
        self.bStop = True
        while self.bExitWorkFunc == False:
            time.sleep(3)
        self.tHandle = None

    def __del__(self):
        self.stop_work()