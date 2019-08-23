from random import randint
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django import http
from libs.captcha.captcha import captcha
from meiduo_mall.settings.dev import logger

#图片验证
from utils.response_code import RETCODE


class ImageCodeView(View):

    def get(self,request, uuid):
        text,image = captcha.generate_captcha()
        redis_client = get_redis_connection('verify_image_code')

        redis_client.setex(uuid, 300, text)

        return http.HttpResponse(image,content_type='image/jpeg')
#短信验证
class SMSCodeView(View):

    def get(self,request,mobile):
        #获取图形验证码的值
        uuid = request.GET.get('image_code_id')
        image_code = request.GET.get('image_code')
        #获取数据库中图形验证码的值
        image_redis_client = get_redis_connection('verify_image_code')
        redis_image_code = image_redis_client.get(uuid)
        #进行托图片验证码对比
        if redis_image_code is None:
            return http.JsonResponse({'code':'4001','errmsg':'图形验证码失效了'})
        #删除uuid
        try :
            image_redis_client.delete('uuid')
        except Exception as e:
            logger.error(e)


        if image_code.lower() != redis_image_code.decode().lower():
            return http.JsonResponse({'code':'4001','errmsg':'输入图形验证码有误'})
        #随机生成六位随机码
        sms_cod = '%06d' % randint(0,999999)
        sms_redis_cilent = get_redis_connection('sms_code')
        sms_redis_cilent.setex(mobile,300,sms_cod)
        #获取频繁发送短信的标识
        send_flag = sms_redis_cilent.get('send_flag_%s' % mobile)
        print(send_flag)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})
        #重新写入send_flag的值，设置过期时间为60s
        #管道写法
        p1 = sms_redis_cilent.pipeline()
        p1.setex('send_flag_%s' % mobile, 60, 1)
        p1.setex('sms_%s' % mobile, 60, sms_cod)
        p1.execute()
        # sms_redis_cilent.setex('send_flag_%s' % mobile,60,1)
        # sms_redis_cilent.setex('sms_%s' % mobile, 60, sms_cod)
        #通过第三方软件发送手机验证码
        #异步触发任务
        from celery_tasks.sms.tasks import ccp_send_sms_code
        ccp_send_sms_code.delay(mobile, sms_cod)
        # from libs.yuntongxun.sms import CCP
        # CCP().send_template_sms(18742078950,[sms_cod,5],1)
        print('当前验证码是',sms_cod)

        return http.JsonResponse({'code':'0','errmsg':'发送短信成功'})




