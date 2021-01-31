import json
import traceback
import uuid
import datetime

import xlrd
from decimal import *

from django.core import serializers
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.http.response import HttpResponse
from django.shortcuts import render

from decimal import Decimal, getcontext, setcontext

# Create your views here.
from fund import models

from .models import FundInfo, FundPartInfo, StockInfo

CONTENT_TYPE_JSON = 'application/json'

def delete_fund(request):
    data = request.POST
    for id in data["ids"].split(","):
        models.FundInfo.objects.get(id=id).delete()
    res = {'code': 200}
    return HttpResponse(json.dumps(res), content_type=CONTENT_TYPE_JSON)

def update_fund(request):
    data = json.loads(request.body)
    obj = models.FundInfo.objects.get(id=data["id"])
    obj.__dict__.update(**data)
    obj.save()
    res = {'code': 200}
    return HttpResponse(json.dumps(res), content_type=CONTENT_TYPE_JSON)

def post_fund(request):
    data = json.loads(request.body)
    data['id'] = uuid.uuid1()
    models.FundInfo.objects.create(**data)
    res = {'code' : 200}
    return HttpResponse(json.dumps(res), content_type= CONTENT_TYPE_JSON)

def get_fund(request):
    data = request.POST
    id = data["id"]
    obj = models.FundInfo.objects.get(id=id)
    data = serializers.serialize('python',[obj])
    res = {
        "code" : 200,
        'data' : data
    }
    return HttpResponse(json.dumps(res,cls=DjangoJSONEncoder),content_type= CONTENT_TYPE_JSON)

def getpage_fund(request):
    data = request.POST
    page_index = data['pageIndex']
    page_size = data['pageSize']

    fund_list = FundInfo.objects.all()
    paginator = Paginator(fund_list, page_size)  # Show 25 contacts per page
    record_count = paginator.count

    try:
        funds = paginator.page(page_index)
        # todo: 注意捕获异常
    except PageNotAnInteger:
        # 如果请求的页数不是整数, 返回第一页。
        funds = paginator.page(1)
    except InvalidPage:
        # 如果请求的页数不存在, 重定向页面
        return HttpResponse('找不到页面的内容')
    except EmptyPage:
        # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
        funds = paginator.page(paginator.num_pages)

    data_list = []
    for fund in funds.object_list:
        fund.pe_low = str(Decimal(fund.pe_low).quantize(Decimal('0.0')))
        fund.pe_normal = str(Decimal(fund.pe_normal).quantize(Decimal('0.0')))
        fund.pe_high = str(Decimal(fund.pe_high).quantize(Decimal('0.0')))
        fund.pe = str(Decimal(fund.pe).quantize(Decimal('0.00')))

        data_list.append(fund)

    funds_data = serializers.serialize("python", data_list, ensure_ascii=False)

    res = {'code': 200,'data':{
        'recordCount' : record_count,
        'records' : funds_data
    }}
    return HttpResponse(json.dumps(res), content_type=CONTENT_TYPE_JSON)


def getpage_fundpart(request):
    data = request.POST
    page_index = data['pageIndex']
    page_size = data['pageSize']
    index_id = data["indexid"]

    fund_list = FundPartInfo.objects.filter(fund_id=index_id)
    paginator = Paginator(fund_list, page_size)  # Show 25 contacts per page
    record_count = paginator.count

    try:
        funds = paginator.page(page_index)
        # todo: 注意捕获异常
    except PageNotAnInteger:
        # 如果请求的页数不是整数, 返回第一页。
        funds = paginator.page(1)
    except InvalidPage:
        # 如果请求的页数不存在, 重定向页面
        return HttpResponse('找不到页面的内容')
    except EmptyPage:
        # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
        funds = paginator.page(paginator.num_pages)

    data_list = []
    for fund in funds.object_list:
        data = {}
        data["name"] = fund.name
        data["code"] = fund.code
        data["ratio"] = str(Decimal(fund.ratio).quantize(Decimal('0.00')))
        data["pe_ttm"] = str(Decimal(fund.pe_ttm).quantize(Decimal('0.00')))
        data["created_time"] = fund.created_time.strftime('%Y/%m/%d %H:%M')

        data_list.append(data)

    # funds_data = serializers.serialize("python", data_list, ensure_ascii=False)
    funds_data = json.dumps(data_list)

    res = {'code': 200, 'data': {
        'recordCount': record_count,
        'records': funds_data
    }}
    return HttpResponse(json.dumps(res), content_type=CONTENT_TYPE_JSON)

def import_fundpart(request):
    data = request.POST
    code = data['code'] #获取指数代码
    index_id = data['indexid']#关联指数id

    file_obj = request.FILES.get('file')
    type_excel = file_obj.name.split('.')[1]

    res = {}

    if 'xls' == type_excel:
        # 开始解析上传的excel表格
        wb = xlrd.open_workbook(filename=None, file_contents=file_obj.read())
        table = wb.sheets()[0]
        nrows = table.nrows  # 行数
        # ncole = table.ncols  # 列数
        try:
            # 先删除同代码下的成分股
            models.FundPartInfo.objects.filter(fund_id=index_id).delete()

            # 正常的数据库操作应该是原子性操作
            with transaction.atomic():

                for i in range(1, nrows):
                    # i/o
                    row_value = table.row_values(i)  # 一行的数据

                    indexn_date = xlrd.xldate_as_tuple(row_value[0], 0);
                    z = indexn_date[0]
                    x = indexn_date[1]
                    c = indexn_date[2]

                    customer_obj = models.FundPartInfo.objects.create(
                        name = row_value[5],
                        code = row_value[4],
                        fund_id = index_id,
                        ratio = row_value[8],
                        pe_ttm = 0.0,
                        created_time = datetime.datetime(z,x,c)
                    )

        except Exception as e:
            res["code"] = 500
            return HttpResponse(json.dumps(res), content_type=CONTENT_TYPE_JSON)

    res["code"] = 200
    return HttpResponse(json.dumps(res), content_type=CONTENT_TYPE_JSON)

#股票信息相关接口
def getpage_stock(request):
    data = request.POST
    page_index = data['pageIndex']
    page_size = data['pageSize']

    fund_list = StockInfo.objects.all()
    paginator = Paginator(fund_list, page_size)  # Show 25 contacts per page
    record_count = paginator.count

    try:
        funds = paginator.page(page_index)
        # todo: 注意捕获异常
    except PageNotAnInteger:
        # 如果请求的页数不是整数, 返回第一页。
        funds = paginator.page(1)
    except InvalidPage:
        # 如果请求的页数不存在, 重定向页面
        return HttpResponse('找不到页面的内容')
    except EmptyPage:
        # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
        funds = paginator.page(paginator.num_pages)

    data_list = []
    for fund in funds.object_list:
        data = {}
        data["name"] = fund.name
        data["code"] = fund.code
        data["net_earning"] = str(Decimal(fund.net_earning).quantize(Decimal('0.00'))) if fund.net_earning else "0.0"
        data["price"] = str(Decimal(fund.price).quantize(Decimal('0.00'))) if fund.price else "0.0"
        # data["pe_ttm"] = str(Decimal(fund.pe_ttm).quantize(Decimal('0.00')))
        data["created_time"] = fund.created_time.strftime('%Y/%m/%d %H:%M')
        data_list.append(data)

    funds_data = json.dumps(data_list)

    res = {'code': 200,'data':{
        'recordCount' : record_count,
        'records' : funds_data
    }}
    return HttpResponse(json.dumps(res), content_type=CONTENT_TYPE_JSON)


def import_stockinfo(request):
    data = request.POST

    file_obj = request.FILES.get('file')
    type_excel = file_obj.name.split('.')[1]

    res = {}
    if 'xls' == type_excel:
        # 开始解析上传的excel表格
        wb = xlrd.open_workbook(filename=None, file_contents=file_obj.read())
        table = wb.sheets()[0]
        nrows = table.nrows  # 行数
        # ncole = table.ncols  # 列数
        try:
            # 先删除同代码下的成分股
            models.StockInfo.objects.all().delete()

            # 正常的数据库操作应该是原子性操作
            with transaction.atomic():

                for i in range(1, nrows):
                    # i/o
                    row_value = table.row_values(i)  # 一行的数据
                    print(row_value[5],row_value[6]);

                    customer_obj = models.StockInfo.objects.create(
                        name = row_value[2],
                        code = row_value[1],
                        pe_ttm = Decimal.from_float(0.0),
                        net_earning = row_value[5],
                        price = row_value[6],
                        created_time = datetime.datetime.now()
                    )

        except Exception as e:
            traceback.print_exc()
            res["code"] = 500
            return HttpResponse(json.dumps(res), content_type=CONTENT_TYPE_JSON)

    print("cccc")
    res["code"] = 200
    return HttpResponse(json.dumps(res), content_type=CONTENT_TYPE_JSON)

def caculate(request):

    #获取股票市盈率
    stocks = models.StockInfo.objects.all()
    stockprice_dict = {}
    stockearning_dict = {}
    for stock in stocks:
        stockprice_dict[stock.code] = stock.price
        stockearning_dict[stock.code] = stock.net_earning

    data = request.POST

    #获取指数
    for id in data["ids"].split(","):
        fund = models.FundInfo.objects.get(id=id)
        price_all = Decimal.from_float(0.0)
        earning_all = Decimal.from_float(0.0)

        #获取成分股
        parts = models.FundPartInfo.objects.filter(fund_id=fund.id)
        for part in parts:
            ratio = part.ratio

            price = stockprice_dict.setdefault(part.code,Decimal.from_float(0.0))
            price_all += ratio*price

            net_earning = stockearning_dict.setdefault(part.code, Decimal.from_float(0.0))
            earning_all += ratio*net_earning

        print(earning_all,price_all);

        fund.pe = price_all / earning_all
        fund.save()

    res = {'code': 200}
    return HttpResponse(json.dumps(res), content_type=CONTENT_TYPE_JSON)
