def get_breadcrumb(cat3):
    #根据三级类别获取二级类别
    cat2 = cat3.parent
    #根据二级类别获取一级类别
    cat1 = cat2.parent
    #拼接前端需要的数据格式
    breadcrumb = {
        'cat1' : {
            'url' :1
        }
    }
