from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from apps.areas.models import Area
from meiduo_mall.settings.dev import logger
from utils.response_code import RETCODE

#01、查询收货地址（省级地址与市级地址）
class AreasView(View):
    #请求方式get
    def get(self, request):
        #获取area_id 如果前段没有传入id则表示需要获得省份信息，如果传入则需要获得市区信息
        area_id = request.GET.get('area_id')
        if not area_id:
            # 读取省份缓存数据
            province_list = cache.get('province_list')
            #查询省份数据
            try:
                province_model_list = Area.objects.filter(parent__isnull=True)
                #序列化省级数据
                province_list = []
                for province_model in province_model_list:
                    province_list.append({'id':province_model.id,'name':province_model.name})
            except Exception as e:
                logger.error(e)
                return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '省份数据错误'})
            #把数据返回给前端
            # 存储省份缓存数据
            cache.set('province_list', province_list, 3600)
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
        else:
            # 读取市或区缓存数据
            sub_data = cache.get('sub_area_' + area_id)
            if not sub_data:
            #查询市级数据
                try:
                    parent_model = Area.objects.get(id=area_id)
                    #根据id获取所有市级数据
                    sub_model_list = parent_model.subs.all()
                    sub_list = []
                    #把所有市级数据添加到列表中
                    for sub_model in sub_model_list:
                        sub_list.append({'id': sub_model.id, 'name': sub_model.name})

                    sub_data = {
                        'id':parent_model.id,
                        'name':parent_model.name
        ,                   'subs':sub_list
                    }
                except Exception as e:
                    logger.error(e)
                    return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市或区数据错误'})
                #返回市级数据
                cache.set('sub_area_' + area_id, sub_data, 3600)
                return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
#02、新增收货地址
