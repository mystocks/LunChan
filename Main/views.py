# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import numpy as np
import pandas as pd
from pandas import DataFrame as DF

import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
#rootPath += "\\DataFunc\\"
rootPath += "//DataFunc//"
sys.path.append(rootPath)

#rootPath = os.path.dirname(os.getcwd())

print("the path is ", rootPath)
#sys.path.append(rootPath)
import getStocksData
import json
# Create your views here.

def recv_data(request):
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        return received_json_data
    else:
        print(None)

def getMyZXG(request):
    #get request
    goods_Id=['603999','002657','600836','601628', '300104', '601038', '000517', '600333', '600917']
    detail = {}
    result = {}
    context = {}

    detail['GoodsId'] = goods_Id
    result['code'] = 0
    context['detail'] = detail
    context['result'] = result
    return JsonResponse(context, safe=False)

def getNewPrice(request):
    '''
    获取指数或者股票的最新价格数据
    :param request:
    :return:
    '''
    req = recv_data(request)

    if req == None:
        return None

    mGetData=getStocksData.getStocksData
    context = {}
    
    req_fields=req['req_fields']
    #req_fields=[-1,4,-140,-120,-20005]
    
    # 获取要请求的字段
    name=req_fields[0]
    ZXJ=req_fields[1]
    ZDF=req_fields[2]
    ZHANGDIE=req_fields[3]
    TINGPAI=req_fields[4]
    
    #第3列是涨跌百分比，4列涨跌幅
    #customDetail=[['上证指数',9.6, 12,100, 5]];
    customDetail=[]

    stockIdList=req['goods_id']

    for id in stockIdList:
        #print id
        
        data=[]#一只股票的实时信息
        result=mGetData.getRealTimeData_from_Network("" + id)
        name=result.loc[0, 'name']
        #print name
        prePrice=float(result.loc[0, 'pre_close'])
        newPrice=float(result.loc[0, 'price'])
        #print type(prePrice),prePrice
        zd=newPrice - prePrice
        zdf=(zd * 100.0) / prePrice
        data.append(name)
        data.append(newPrice*1000)
        data.append(zdf*100)
        data.append(zd*1000)
        data.append(5)
        data2={}
        data2['goods_Id']=result.loc[0, 'code']
        data2['rep_field_value']=data
        customDetail.append(data2)

    context['quota_value']=customDetail
    context['rep_fields']=req_fields
    context['total_size']=len(customDetail)
    return JsonResponse(context, safe=False)

def getZXG_Recommend(request):
    '''
    获取个人自选股列表并返回
    :param request:
    :return:
    '''
    context = {}
    return JsonResponse(context, safe=False)

#getZixuan(None)

def getUserId(request):
    dataAttr = {}
    dataAttr['detail']='testaaa'
    dataAttr['result']={'code':0}
    return JsonResponse(dataAttr, safe=False)
    
def getOneQuotation(request):
    rev = recv_data(request)
    if rev == None:
        return None
    mGetData = getStocksData.getStocksData
    context = {}
    req_fields = rev['req_fields']
    good_id = rev['goods_id']
    good_id = '603999'
    result = mGetData.getRealTimeData_from_Network("" + good_id)
    print(result)

def Main(request):
    context = {}
    context['hello'] = 'Hello World!'
    return render(request, 'base.html')

def getOneData(request):
    mGetData = getStocksData.getStocksData
    stockId=request.GET.get('stockId', "603999")
    retList=mGetData.get_one_data_form_databases(stockId)
    dataAttr=retList[-100:]
    print(len(retList),stockId)
    return JsonResponse(dataAttr, safe=False)

def KXian(request):
    #mGetData = getStocksData.GetStocksAllData()
    mGetData=getStocksData.getStocksData
    data=mGetData.get_one_data_form_databases("600025")
    idList=mGetData.get_all_stock_id_from_database()
    #return
    '''
    dataArr = [["2017/10/1", 2320.26,2302.6,2287.3,2362.94],]
    '''
    dataArr=data[-100:]
    print(dataArr)
    context = {}
    # js中使用{{hello|safe}}获取
    one=json.dumps(dataArr)
    id=json.dumps(idList)
    context['oneData']=one
    context['allId']=id
    return render(request, 'KXian.html', context)