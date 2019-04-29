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


#��ʾweb������������
@login_required
def app_testcase_page(request):
    username = request.session.get('user', '')
    appcases = Appcase.objects.get_queryset().order_by('id')
    paginator = Paginator(appcases, 12)  # ����paginator����,����ÿҳ��ʾ15����¼
    page = request.GET.get('page', 1)  # ��ȡ��ǰҳΪ��1ҳ
    currentPage = int(page)  # �ѵ�ǰҳת��������
    try:
        appcases = paginator.page(page)  # ��ȡ��ǰҳ�����ļ�¼�б�
    except PageNotAnInteger:
        appcases = paginator.page(1)  # ��������ҳ��������������ʾ��1ҳ����
    except EmptyPage:
        appcases = paginator.page(paginator.num_pages)  # �������ĵ�ҳ������ϵͳ��ҳ���У�����ʾ���һҳ
    return render(request, "App_test_robotframework.html", {"user": username, "webcases": appcases})
