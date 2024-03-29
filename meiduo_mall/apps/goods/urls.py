"""meiduo_mall URL Configuration

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
from . import views
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'register/$', views.RegisterView.as_view()),
    # url(r'^index/$',views.IndexView.as_view(),name='index'),

    #商品列表页
    url(r'list/(?P<category_id>\d+)/(?P<page_num>\d+)/', views.ListView.as_view(),name='list'),
    #热销排行
    url(r'hot/(?P<category_id>\d+)/', views.HotGoodsView.as_view()),
    #商品详情页
    url(r'detail/(?P<sku_id>\d+)/', views.DetailView.as_view(),name='detail'),
    #统计访问量
    url(r'detail/visit/(?P<category_id>\d+)/', views.DetailVisitView.as_view()),


]
