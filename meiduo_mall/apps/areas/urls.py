
from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'register/$', views.RegisterView.as_view()),
    #查询收货地址
    url(r'areas/$',views.AreasView.as_view()),

]
