from celery_tasks.main import app
@app.task
def ccp_send_sms_code(mobile, sms_cod):
    from libs.yuntongxun.sms import CCP
    result = CCP().send_template_sms(18742078950,[sms_cod,5],1)
    print(sms_cod)

    return result