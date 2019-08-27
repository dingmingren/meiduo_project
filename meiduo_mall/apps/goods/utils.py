import pickle
import base64
def get_breadcrumb(cat3):
    #根据三级类别获取二级类别
    cat2 = cat3.parent
    #根据二级类别获取一级类别
    cat1 = cat2.parent
    #拼接前端需要的数据格式
    # 因为前端需要url属性，而三级分类表只有id与name属性，所以动态添加url属性
    # 频道组---频道表（group_id,category_id）---三级分类表
    # 获取所有频道
    cat1.url = cat1.goodschannel_set.all()[0].url
    breadcrumb = {

        'cat1' : {
            "url": cat1.goodschannel_set.all()[0].url,
            'name': cat1.name
        },
        'cat2' : cat2,
        'cat3' : cat3,
    }
    return breadcrumb
#封装base64加密类
class CookieSecret(object):
    #加密
    @classmethod
    def dumps(cls, data):
        #1、讲数据转换成bytes
        data_bytes = pickle.dumps(data)
        #2、讲byte进行序列化加密
        base64_bytes = base64.b64encode(data_bytes)
        #3、将加密完的bytes以字符串的形式进行输出
        base64_str = base64_bytes.decode()

        #返回数据
        return base64_str
    @classmethod
    def loads(cls, data):
        #1、将数据解密转成bytes
        base64_bytes = base64.b64decode(data)
        #2、将bytes转回成为原来的python数据类型
        pickle_data = pickle.loads(base64_bytes)

        return pickle_data
