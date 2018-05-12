# -*- coding:utf-8 -*-
import os
import MySQLdb

class MySqlBase(object):
    mConnect=None
    mCursor=None
    mInited=False

    def __init__(self, host, user, passwd, charset):
        '''
        :param host:主机地址，本机为localhost
        :param user: 用户名,root
        :param passwd: 密码为空或者Root@123
        :param charset: utf8,不能写成utf-8
        '''
        self.host = host
        self.user = user
        self.passwd = passwd
        self.charset = charset
        
        self.connect=MySQLdb.connect(host = self.host, user = self.user, passwd = self.passwd, charset = self.charset)
        if self.mConnect != None:
            self.mCursor = self.mConnect.cursor()
            self.mInited = True
            print("connected to localhost MySql!")
    
    def selectDb(self, dbName):
        if self.mInited:
            try:
                self.mConnect.selectDb(dbName)
            except Exception as e:
                print("****ERROR:try to selectDb failed;")
                print("****ExceptionInfo:", str(e))
                return False
        return True

    def executeCmdline(self, cmdline):
        if self.mInited == False or cmdline == None or len(cmdline) == 0:
            return False
        try:
            self.mCursor.execute(cmdline)
        except Exception as e:
            print("****ERROR:execute Failed cmd=:", cmdline)
            print("****ExceptionInfo:", str(e))
            return False
        return True

    def createDb(self, dbName, bDropExist = False):
        try:
            cmdLine = "drop database if exists %s"%dbName
            self.mCursor.execute(cmdLine)
            cmdLine="create database %s"%dbName
            self.mCursor.execute(cmdLine)
        except Exception as e:
            print("****ERROR:createDb Failed")
            print("****ExceptionInfo:", str(e))

    def queryData(self, tableName, count):
        '''
        :param tableName: 表名称
        :param count: 读取的数量
        :return:返回查询结果
        '''
        result = None
        if self.mInited == False or tableName == None:
            return result
        try:
            result = self.mCursor.execute("select * from %s;" % tableName)
        except Exception as e:
            print("****ERROR:query data failed,tableName=", tableName)
            print("****ExceptionInfo:", str(e))
            return None
        return result
        
    def __del__(self):
        if self.mInited:
            self.mConnect.close()
            self.mInited = False
