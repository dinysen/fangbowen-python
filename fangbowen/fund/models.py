import uuid

from django.db import models


# 基金信息表
class FundInfo(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid1,editable=False,null=False)
    name = models.CharField(max_length=200, verbose_name="指数名称")
    code = models.CharField(max_length=200, verbose_name="指数代码")
    pe_low = models.DecimalField( max_digits=20, decimal_places=10, verbose_name="低估值")
    pe_normal = models.DecimalField(max_digits=20, decimal_places=10, verbose_name="正常值")
    pe_high = models.DecimalField(max_digits=20, decimal_places=10, verbose_name="高估值")
    pe = models.DecimalField(max_digits=20, decimal_places=10, verbose_name="现估值",null=True)

    def __str__(self):
        message = "name:"+self.name
        return message

    class Meta:
        verbose_name = verbose_name_plural  = "基金信息"


#指数成分股表
class FundPartInfo(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False, null=False)
    name = models.CharField(max_length=200, verbose_name="股票名称")
    code = models.CharField(max_length=200, verbose_name="股票代码")
    fund_id = models.CharField(max_length=200, verbose_name="所属指数",null=True)
    ratio = models.DecimalField(max_digits=20, decimal_places=10, verbose_name="占比")
    pe_ttm = models.DecimalField(max_digits=20, decimal_places=10, verbose_name="TTM市盈率")
    created_time = models.DateTimeField( verbose_name="导入时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = verbose_name_plural = "指数成分股"

class StockInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False, null=False)
    name = models.CharField(max_length=200, verbose_name="股票名称")
    code = models.CharField(max_length=200, verbose_name="股票代码")
    pe_ttm = models.DecimalField(max_digits=30, decimal_places=5, verbose_name="TTM市盈率",null=True)
    net_earning = models.DecimalField(max_digits=30, decimal_places=5, verbose_name="净利润",null=True)
    price = models.DecimalField(max_digits=30, decimal_places=5, verbose_name="总市值",null=True)
    created_time = models.DateTimeField( verbose_name="导入时间")