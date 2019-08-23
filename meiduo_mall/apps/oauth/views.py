from django.shortcuts import render
from django.db import models
from django.views import View
from QQLoginTool.QQtool import OAuthQQ

class QQAuthURLView(View):
    def get(self, request):
        pass