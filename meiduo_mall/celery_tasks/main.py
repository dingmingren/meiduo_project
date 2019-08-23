#1、导包
from celery import Celery
#2、加载项目配置文件
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

#3、实例化
app = Celery('celery_tasks')

#4、加载celery配置文件
app.config_from_object('celery_tasks.config')
#5、celery加载任务
#发短信任务
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])
#发邮件任务
# app.autodiscover_tasks(['celery_tasks.email'])