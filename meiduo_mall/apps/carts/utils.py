import json
from apps.goods.utils import CookieSecret
from django_redis import get_redis_connection
def merge_cart_cookie_to_redis(request,user,response):
    #1、获取cookie数据
    cookie_str = request.COOKIES.get('carts')

    #2、如果没有数据，就直接响应结果
    if not cookie_str:
        return response
    #3、解密
    cookie_dict = CookieSecret.loads(cookie_str)

    #4、合并购物车数据
    carts_redis_client = get_redis_connection('carts')
    carts_data = carts_redis_client.hgetall(user.id)
    carts_dict = {}

    #将carts_data二进制字典转换成为普通字典
    for data in carts_data.items():
        sku_id = int(data[0].decode())
        cart_dict = json.loads(data[1].decode())
        carts_dict[sku_id] = cart_dict

    #更新数据
    carts_dict.update(cookie_dict)

    #修改redis数据
    for sku_id in carts_dict.keys():
        carts_redis_client.hset(user.id,sku_id,json.dumps(carts_dict[sku_id]))

    #删除cookie的值
    response.delete_cookie('carts')

    return response

