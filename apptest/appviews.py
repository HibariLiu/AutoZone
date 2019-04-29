from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import auth
from django.contrib import messages
from django.core.paginator import  Paginator, EmptyPage, PageNotAnInteger
from apptest.models import Appcasestep,Appcase,Appcase_keywords,apptest_task
from django.core.paginator import  Paginator, EmptyPage, PageNotAnInteger
import os
import pyautogui
from webtest.tasks import write_name_txt,readSQLCounts,get_task_stepdata,getcasename_from_SQL,get_webtask_times
import time
from  webtest.get_webcase_stepdata import readwebcaseSQL,write_to_txt,remove_webtest_txt,run_in_terminal

# Create your views here.


#显示web测试用例界面
@login_required
def app_testcase_page(request):
    username = request.session.get('user', '')
    appcases = Appcase.objects.get_queryset().order_by('id')
    paginator = Paginator(appcases, 12)  # 生成paginator对象,设置每页显示15条记录
    page = request.GET.get('page', 1)  # 获取当前页为第1页
    currentPage = int(page)  # 把当前页转换成整数
    try:
        appcases = paginator.page(page)  # 获取当前页码数的记录列表
    except PageNotAnInteger:
        appcases = paginator.page(1)  # 如果输入的页数不是整数则显示第1页内容
    except EmptyPage:
        appcases = paginator.page(paginator.num_pages)  # 如果输入的的页数不在系统的页数中，则显示最后一页
    return render(request, "App_test_robotframework.html", {"user": username, "webcases": appcases})
