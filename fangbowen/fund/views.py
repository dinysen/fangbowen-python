import json
import uuid
from decimal import *

from django.core import serializers
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.
from fund import models

from .models import FundInfo

CONTENT_TYPE_JSON = 'application/json'

def post_fund(request):
    data = json.loads(request.body)
    data['id'] = uuid.uuid1()
    models.FundInfo.objects.create(data)
    res = {'code' : 200}
    return HttpResponse(json.dumps(res), content_type= CONTENT_TYPE_JSON)

def get_fund(request):
    data = serializers.serialize('python',models.FundInfo.objects.all())
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