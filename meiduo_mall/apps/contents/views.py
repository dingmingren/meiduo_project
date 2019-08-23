from django.shortcuts import render
from django.views import View

from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories



class IndexView(View):
    def get(self,request):
        categories = get_categories()
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')


        context = {
            'categories': categories,
            'contents': contents,
        }
        return render(request, 'index.html', context)
# Create your views here.

