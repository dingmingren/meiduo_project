from django.shortcuts import render
from django.views import View

#1、商品列表页
class ListView(View):

    def get(self,request,category_id, page_num):

        return render(request,'list1.html')

