from django import http
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound
from django.http import HttpResponseServerError
from django.shortcuts import render
from django.views import View

#1、商品列表页
from apps.contents.utils import get_categories
from apps.goods.models import GoodsCategory, SKU
from apps.goods.utils import get_breadcrumb

#1、热销排行
from utils.response_code import RETCODE
class HotGoodsView(View):
    def get(self,request,category_id):
        skus = SKU.objects.filter(category=category_id, is_launched=True).order_by('-sales')
        # 取前两个
        hot_skus = skus[:2]
        # 因为销量实时改变，所以热销排行实时更新，应该做成局部刷新的形式
        # 序列化
        hot_list = []
        for sku in hot_skus:
            hot_list.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_list})

#2、列表页展示
class ListView(View):

    def get(self,request,category_id, page_num):

        #1、商品频道分类
        categories = get_categories()
        cat3 = GoodsCategory.objects.get(id=category_id)
        #2、面包屑组件
        breadcrumb = get_breadcrumb(cat3)

        #3、排序
        #接收参数
        sort = request.GET.get('sort')
        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = '-sales'
        else:
            sort_field = 'create_time'
        skus = SKU.objects.filter(category=cat3,is_launched=True).order_by(sort_field)
        #4、分页
        #一页显示几个
        paginator = Paginator(skus,5)
        #总页数
        all_pages = paginator.num_pages
        #当前页显示的内容
        page_skus = paginator.page(page_num)
        #5、热销商品排行
        #按照销量排序

        #返回给前端的数据

        context = {
            'categories':categories,
            'breadcrumb':breadcrumb,
            'sort': sort,  # 排序字段
            'category': cat3,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': all_pages,  # 总页数
            'page_num': page_num,  # 当前页码
        }
        return render(request,'list.html',context)


#3、商品详情页
class DetailView(View):
    def get(self, request, sku_id):
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }
        return render(request, 'detail.html', context)

#4、商品访问量
class DetailVisitView(View):
    def post(self, request, category_id):
        try:
            #1、校验三级分类是否存在
            category = GoodsCategory.objects.get(id=category_id)

        except Exception as e:
            return HttpResponseNotFound('缺少必传参数')
            #2、查询日期数据,根据日期判断，记录是否存在

        from datetime import datetime
        # 将日期按照格式转换成字符串（将日期转换成制定格式）
        today_str =  datetime.now().strftime('%Y-%m-%d')
        # 将字符串再转换成日期格式,方便与时间字段做对比
        today_date = datetime.strptime(today_str,'%Y-%m-%d')

        from apps.goods.models import GoodsVisitCount
        try:
            # 3.如果有当天商品分类的数据  就累加数量
            count_data = category.goodsvisitcount_set.get(date=today_date)
        except:
            # 4. 没有, 就新建之后在增加
            count_data = GoodsVisitCount()

        try:
            count_data.count += 1
            count_data.category = category
            count_data.save()
        except Exception as e:
            return HttpResponseServerError('新增失败')

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

