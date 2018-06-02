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
# 自动适配windows和linux反斜杠
rootPath = os.path.join(rootPath, "DataFunc")
sys.path.append(rootPath)

#rootPath = os.path.dirname(os.getcwd())

print("the path is ", rootPath)
#sys.path.append(rootPath)
import getStocksData
import json
# Create your views here.

# debug开关
g_debug = 0
def createDebugParams():
    reqIds = ['603999']
    reqFileds = ['price', 'zdf', 'zhangdie', 'open', 'high', 'low', 'hsl', 'syl', 'sjl', 'volume', 'jl', 'zsz', 'amount', 'lb', 'ltsz', 'suspension']
    data = {}
    data['class_type'] = 4
    data['group_type'] = 0
    data['goods_id'] = reqIds
    data['req_fields'] = reqFileds
    data['sort_field'] = -9999
    data['sort_order'] = True
    data['req_begin'] = 0
    data['req_size'] = 0
    data['last_update_market_time'] = 0
    data['last_update_market_date'] = 0
    return data

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.int32):
            return int(obj)
        elif isinstance(obj, np.int64):
            return int(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

def recv_data(request):
    if g_debug != 0:
        return createDebugParams()

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

    #第3列是涨跌百分比，4列涨跌幅
    #customDetail=[['上证指数',9.6, 12,100, 5]];
    customDetail=[]

    stockIdList=req['goods_id']

    for id in stockIdList:
        
        data=[]#一只股票的实时信息
        result=mGetData.getRealTimeData_from_Network("" + id)
        data = mGetData.getDataByReqFiled(str(id), req_fields)
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

    data = mGetData.getDataByReqFiled(str(good_id[0]), req_fields)
    customDetail=[]
    data2={}
    data2['goods_Id']=good_id[0]
    data2['rep_field_value']=data
    customDetail.append(data2)

    context['quota_value']=customDetail
    context['rep_fields']=req_fields
    context['total_size']=len(customDetail)
    ret = json.dumps(context, cls=MyEncoder)
    #return JsonResponse(context.tolist(), safe=False)
    return HttpResponse(ret)

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