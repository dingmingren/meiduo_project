from collections import OrderedDict

from apps.goods.models import GoodsChannel


def get_categories():
    categories = OrderedDict()
    # 1、获取37个频道
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    # 2、遍历37个频道
    for channel in channels:
        # 2.1 根据频道，获取频道组id
        group_id = channel.group_id
        # 2.2 分组判断11个组
        if not group_id in categories:
            categories[group_id] = {'channels': [], 'sub_cats': []}
        # 3、从频道，根据当前category_id获取一级分类
        cat1 = channel.category
        # 动态添加url的属性
        cat1.url = channel.url
        categories[group_id]['channels'].append(cat1)

        # 4、二级分类，一级分类.subs.all()
        for cat2 in cat1.subs.all():
            cat2.sub_cats = []

            # 5、三级分类，二级分类.subs.all()
            for cat3 in cat2.subs.all():
                cat2.sub_cats.append(cat3)
            categories[group_id]['sub_cats'].append(cat2)

    return categories