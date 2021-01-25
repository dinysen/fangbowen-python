import uuid

from django.db import models


# 基金信息表
class FundInfo(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid1,editable=False,null=False)
    name = models.CharField(max_length=200, verbose_name="基金名称")
    code = models.CharField(max_length=200, verbose_name="基金代码")
    pe_low = models.DecimalField( max_digits=6, decimal_places=3, verbose_name="市盈率低估值")
    pe_normal = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="市盈率正常值")
    pe_high = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="市盈率高估值")
    pe = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="估值")

    def __str__(self):
        message = "id:"+str(self.id)
        message+= "\nname:"+self.name
        message += "\ncode:" + self.code
        message += "\npe_low:" + self.pe_low
        message += "\npe_normal:" + self.pe_normal
        message += "\npe_high:" + self.pe_high
        message += "\npe:"+self.pe
        return message

    class Meta:
        verbose_name = verbose_name_plural  = "基金信息"


#基金成分股表
class FundPartInfo(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False, null=False)
    name = models.CharField(max_length=200, verbose_name="股票名称")
    code = models.CharField(max_length=200, verbose_name="股票代码")
    fund = models.ForeignKey(FundInfo, verbose_name="所述基金",on_delete=models.CASCADE,)
    ratio = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="占比")
    pe_ttm = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="TTM市盈率")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="导入时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = verbose_name_plural = "基金成分股"