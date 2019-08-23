from django.contrib.auth.backends import ModelBackend
import re
from .models import User
#多方式登陆（用户名和手机号）
def get_user_by_account(account):
    try :
        #手机号登陆
        if re.match(r'^1[3-9]\d{9}$',account):
            user = User.objects.get(mobile=account)
        #账号登录
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist :
        return None
    else :
        return user
#获取user对象，并且进行密码校验
#新建类，重写authenticate（）方法
class UsernameMobileAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 根据传入的username获取user对象。username可以是手机号也可以是账号
        user = get_user_by_account(username)
        #校验user是否存在，并且校验密码是否正确
        if user and user.check_password(password):
            return user
