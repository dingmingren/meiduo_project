import json

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django import http
from django_redis import get_redis_connection
import re

from apps.areas.models import Address
from apps.users.models import User
from celery_tasks.email.tasks import send_verify_email
from meiduo_mall.settings.dev import logger
from utils.response_code import RETCODE
#04、邮箱添加和验证
class EmailView(LoginRequiredMixin,View):

    def put(self,request):
        #取出请求参数中的email
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        email = json_dict.get('email')
        #校验email格式是否满足要求
        # if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        #     return http.HttpResponseForbidden('参数email有误')

        #保存email
        try :
            request.user.email = email
            request.user.save()

        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR,'errmsg':'添加邮箱失败'})
        token_value = {
            'user_id': request.user.id,
            'email': email
        }

        from utils.secret import SecretOauth
        secret_str = SecretOauth().dumps(token_value)
        verify_url = settings.EMAIL_ACTIVE_URL + "?token=" + secret_str
        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(email, verify_url)

        # 4. 返回前端结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})
        #返回响应数据给前端

        #注册成功开始发送邮件
#03、用户中心
class UserInfoView(LoginRequiredMixin,View):
    """用户中心"""

    def get(self, request):
        """提供个人信息界面"""
        #获取用户的个人信息（用户名手机等）
        context = {
            'username':request.user.username,
            'mobile' : request.user.mobile,
            'email':request.user.email,
            'email_active':request.user.email_active
        }
        return render(request, 'user_center_info.html',context=context)
#01、用户登录后端实现
class  LoginView(View):
    def get(self,request):

        return render(request,'login.html')
    #获取前段传送的用户名与密码
    def post(self,request):
        #1、接收三个参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        #2、对接收到的参数进行校验
        #2.1 判断用户名密码是否存在空值，如果存在空值则返回参数不齐全。
        if not all([username,password]):
            return http.HttpResponseForbidden('参数不齐全')
        #2.2 对用户名进行正则校验，判断用户名是否满足长度与字符要求。
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        #2.3 对密码进行正则校验，判断密码的长度与字符要求是否满足。
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')


        #3 通过django自带认证系统authenticate验证用户名与密码
        from django.contrib.auth import authenticate,login
        user = authenticate(username=username,password=password)

        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})
        #4 保持登录状态
        login(request,user)

        #判断是否记住用户名，如果自动记住，则保持会话状态，否则当回话结束session就过期
        if remembered != 'on':
            request.session.set_expiry(0)
        else :
            request.session.set_expiry(None)
        #next重定向到指定页面
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
        #首页用户名展示
            response = redirect(reverse('contents:index'))

        # 注册时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response
#注册页面
class  RegisterView(View):

    def get(self,request):
        return render(request,'register.html')
# Create your views here.
    def post(self,request):
        #获取注册信息
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        #判断注册信息是否存在空值
        if not all([username,password,password2,mobile,allow]):
            return http.HttpResponseForbidden('缺少必传参数')
        #对账号密码进行正则校验
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        if not re.match(r'^[0-9a-zA-Z]{8,20}',password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        if not re.match(r'1[3-9]\d{9}$',mobile):
            return http.HttpResponseForbidden('请输入正确的手机号')
        # 验证手机验证码
        sms_code = request.POST.get('msg_code')
        redis_code_client = get_redis_connection('sms_code')
        redis_code = redis_code_client.get(mobile)
        if redis_code is None:
            return render(request,'register.html',{'sms_code_errmsg':'无效的验证码'})
        if sms_code != redis_code.decode():
            return render(request,'register.html',{'sms_code_errmsg':'输入短信验证码有无'})
        #判断用户是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')
        try:
            user = User.objects.create_user(username=username,password=password,mobile=mobile)
        except DatabaseError:

            return render(request,'register.html',{'register_errmsg':'注册失败'})
        login(request,user)
        return redirect(reverse('contents:index'))
#账号验证
class UsernameCountView(View):
    def get(self,request,username):
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code':RETCODE.OK,'errmsg': 'OK', 'count': count})
#手机号验证
class MobileCountView(View):
    """判断手机号是否重复注册"""

    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})
# class ImageCodeView(View):
#     """图形验证码"""
#
#     def get(self, request, uuid):
#         """
#         :param request: 请求对象
#         :param uuid: 唯一标识图形验证码所属于的用户
#         :return: image/jpg
#         """
#         text,image = captcha.generate_captcha()
#         #2、链接数据库
#         redis_client = get_redis_connection('verify_image_code')
#         #3、存储
#         redis_client.setex(uuid,300,text)
#         return http.HttpResponse(image, content_type='image/jpeg')
#图片验证
# class ImageCodeView(View):
#
#     def get(self,request, uuid):
#         text,image = captcha.generate_captcha()
#         redis_client = get_redis_connection('verify_image_code')
#
#         redis_client.setex(uuid, 300, text)
#
#         return http.HttpResponse(image,content_type='image/jpeg')
# 短信验证
# class SMSCodeView(View):
#
#     def get(self,request,mobile):
#
#         uuid = request.GET.get('image_code_id')
#         image_code = request.GET.get('image_code')
#
#         image_redis_client = get_redis_connection('verify_image_code')
#         redis_image_code = image_redis_client.get('uuid')
#
#         if redis_image_code is None:
#             return http.JsonResponse({'code':'4001','errmsg':'图形验证码失效了'})
#
#         try :
#             image_redis_client.delete('uuid')
#         except Exception as e:
#             logger.error(e)
#
#
#         if image_code.lower() != redis_image_code.decode().lower():
#             return http.JsonResponse({'code':'4001','errmsg':'输入图形验证码有误'})
#
#         sms_cod = '%06d' % randint(0,999999)
#         sms_redis_cilent = get_redis_connection('sms_code')
#         sms_redis_cilent.setex(mobile,300,sms_cod)

        # from libs.yuntongxun.sms import CCP
        # CCP().send_template_sms(18742078950,[sms_cod,5],1)
        # print('当前验证码是',sms_cod)
        #
        # return http.JsonResponse({'code':'0','errmsg':'发送短信成功'})
#02、退出登陆的实现
class LogoutView(View):
    """退出登录"""
    def get(self, request):
        """实现退出登录逻辑"""
        #01、清理session
        logout(request)
        #02、退出登录，重定向到登录页
        response = redirect(reverse('users:login'))
        #03、退出登录时清除cookie中的username
        response.delete_cookie('username')

        return response

class VerifyEmailView(LoginRequiredMixin,View):
    def get(self,request):
        #1.接收参数
        token = request.GET.get('token')
        #2.解密
        from utils.secret import SecretOauth
        json_dict = SecretOauth().loads(token)
        #3.校验，用户是否存在，并且邮箱也正确
        try:
            user = User.objects.get(id=json_dict['user_id'],email=json_dict['email'])
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('无效的token')
        user.email_active = True
        user.save()
        return redirect(reverse('users:info'))

#04、收货地址
class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""

    def get(self, request):
        """提供收货地址界面"""
        #获取用户地址列表
        login_user = request.user
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        address_dict_list = []
        #循环遍历讲地址添加到地址列表中
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)
        #返回数据
        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_dict_list,
        }
        return render(request, 'user_center_site.html',context=context)
#05、增加收货地址
class CreateAddressView(LoginRequiredMixin, View):
    def post(self, request):
    #1、接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        #校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        try:
            #添加地址
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
            #设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()

        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})
        #讲新增的地址返回给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})
#06、修改收货地址
class UpdateDestroyAddressView(LoginRequiredMixin, View):

    def put(self,request,address_id):
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')
        try:
            #判断地址是否存在，并且更新地址信息
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})
        address = Address.objects.get(id=address_id)
        #构造响应数据
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        # 响应更新地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})
    def delete(self,request,address_id):

        try:
            # 获取要删除的地址
            address = Address.objects.get(id=address_id)
            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})
        # 响应删除地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})
#07、设置默认地址
class DefaultAddressView(LoginRequiredMixin,View):
    def put(self,request,address_id):
        try:
            # 接收参数,查询地址
            address = Address.objects.get(id=address_id)

            # 设置地址为默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})

            # 响应设置默认地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})
#08、修改地址标题
class UpdateTitleAddressView(LoginRequiredMixin,View):
    def put(self,request,address_id):
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')
        try:
            # 查询地址
            address = Address.objects.get(id=address_id)

            # 设置新的地址标题
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置地址标题失败'})

            # 4.响应删除地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置地址标题成功'})
#09、修改密码
class ChangePasswordView(LoginRequiredMixin, View):
    def get(self,request):
        #展示修改密码界面
        return render(request, 'user_center_pass.html')
    #修改密码
    def post(self, request):
        old_password = request.POST.get('old_pwd')
        new_password = request.POST.get('new_pwd')
        new_password2 = request.POST.get('new_cpwd')
        if not all([old_password, new_password, new_password2]):
            return http.HttpResponseForbidden('缺少必传参数')
        #检查旧密码是否正确
        result = request.user.check_password(old_password)
        if not result:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '原始密码错误'})
        if new_password != new_password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'change_pwd_errmsg': '修改密码失败'})

            # 清理状态保持信息
        logout(request)
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')

        # # 响应密码修改结果：重定向到登录界面
        return response
