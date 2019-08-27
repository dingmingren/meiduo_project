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
    url(r'^register/$',views.RegisterView.as_view(),name='register'),
    url(r'usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/', views.UsernameCountView.as_view()),
    url(r'mobiles/(?P<mobile>1[3-9]\d{9})/count/', views.MobileCountView.as_view()),
    # url(r'image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
    #登录页面路由
    url(r'login/$', views.LoginView.as_view(),name='login'),
    #退出功能
    url(r'logout/$', views.LogoutView.as_view(),name='logout'),
    # url(r'sms_codes/(?P<mobile>1[3-9]\d{9})/', views.SMSCodeView.as_view()),
    #用户中心路由
    url(r'info/$', views.UserInfoView.as_view(),name='info'),
    #添加邮箱
    url(r'^emails/$', views.EmailView.as_view()),
    #校验邮箱
    url(r'emails/verification/$', views.VerifyEmailView.as_view()),
    #收货地址
    url(r'address/$', views.AddressView.as_view(),name='address'),
    #增加收货地址
    url(r'addresses/create/$', views.CreateAddressView.as_view()),
    #修改地址
    url(r'addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    #删除地址
    # url(r'addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    #设置默认地址
    url(r'addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),
    #修改地址标题
    url(r'addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view()),
    #修改密码
    url(r'password/$', views.ChangePasswordView.as_view(),name='password'),
    #用户浏览记录
    url(r'browse_histories/', views.UserBrowseHistory.as_view()),



]
