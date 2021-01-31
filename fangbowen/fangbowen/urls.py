"""fangbowen URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from fund import views as fund_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    #指数信息相关接口
    url(r'^api/fund/getone', fund_views.get_fund),
    url(r'^api/fund/post', fund_views.post_fund),
    url(r'^api/fund/getpage', fund_views.getpage_fund),
    url(r'^api/fund/update', fund_views.update_fund),
    url(r'^api/fund/delete', fund_views.delete_fund),
    url(r'^api/fund/caculate', fund_views.caculate),

    #成分股相关接口
    url(r'^api/fundpart/getpage', fund_views.getpage_fundpart),
    url(r'^api/fundpart/import', fund_views.import_fundpart),

    #股票相关接口
    url(r'^api/stock/getpage', fund_views.getpage_stock),
    url(r'^api/stock/import', fund_views.import_stockinfo),

]
