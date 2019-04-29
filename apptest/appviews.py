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
from apptest.tasks import write_name_txt,readSQLCounts,get_task_stepdata,getcasename_from_SQL,get_apptask_times
import time
from apptest.get_appcase_stepdata import readappcaseSQL,write_to_txt,remove_apptest_txt,run_in_terminal

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

# #app���������������
@login_required
def add_app_casename(request):
    username = request.session.get('user', '')
    appcases = Appcase.objects.all()
    if request.method == "POST":
        appmodelname = request.POST.get("appmodelname", )
        appcasename = request.POST.get("appcasename", )
        appcharger = request.POST.get("appcharger", )
        appaddcasedesc = request.POST.get("appaddcasedesc", )
        Appcase.objects.get_or_create(appcase_models=appmodelname,appcasename=appcasename,appcase_charger=appcharger,appcasedesc=appaddcasedesc)
        return render(request, "App_test_robotframework.html", {"user": username, "appcases":appcases})


#ɾ��app��������
@login_required
def del_app_casename(request):
    username = request.session.get('user', '')
    appcases =Appcase.objects.all()
    if request.method == "POST":
        appcaseID = request.POST.get("id", )
        Appcase.objects.filter(id=appcaseID).delete()
        return render(request, "App_test_robotframework.html", {"user": username, "appcases":appcases})



#��ʾapp���Բ������
@login_required
def display_app_casesteps(request):
    username = request.session.get('user', '')
    appcaseid = request.GET.get('appcase.id',None)
    appcase = Appcase.objects.get(id=appcaseid)
    appcasesteps = Appcasestep.objects.all()
    return render(request,"appcasestep_manage.html",{"user": username,"appcasesteps":appcasesteps,"appcase":appcase})


#ɾ��web���Բ���
@login_required
def delete_app_casesteps(request):
    appcaseid = request.POST.get("casename_id")
    username = request.session.get('user', '')
    appcase = Appcase.objects.get(id=appcaseid)
    appcasesteps = Appcasestep.objects.all()
    stepid = request.POST.get("step_id")
    Appcasestep.objects.filter(Appcase_id=appcaseid,id=stepid).delete()
    return render(request, "appcasestep_manage.html",{"user": username, "appcasesteps": appcasesteps, "appcase": appcase})


#�ϴ�ͼƬ
@login_required
def upload_file(request):
    # ���󷽷�ΪPOSTʱ�����д���
    if request.method == "POST":
        # ��ȡ�ϴ����ļ������û���ļ�����Ĭ��ΪNone
        File = request.FILES.get("myfile", None)
        if File is None:
            return HttpResponse("û����Ҫ�ϴ����ļ�")
        else:
            #���ض����ļ����ж����Ƶ�д����
            #print(os.path.exists('/temp_file/'))
            with open("./webtest/media/%s" % File.name, 'wb+') as f:
                #�ֿ�д���ļ�
                for chunk in  File.chunks():
                    f.write(chunk)
            return HttpResponse("UPload over!")
    else:
        return  render(request, "test.html")


#����ִ�в�������
@login_required
def maoyan_test(request):
    username = request.session.get('user', '')
    tasks = Appcasestep.objects.all()
    if request.method == "POST":
        upperlevel_id = request.POST.get("casename_id")
        write_to_txt(upperlevel_id)
        time.sleep(1)
        readappcaseSQL(upperlevel_id)
    return render(request, "appcasestep_manage.html",{"user": username, "tasks": tasks})

#����ִ�гɹ��󱣴�
@login_required
def remove_test_txt(request):
    username = request.session.get('user', '')
    tasks = Appcasestep.objects.all()
    if request.method =="POST":
        txtname = request.POST.get("casename_id")
        remove_apptest_txt(txtname)
    return render(request, "appcasestep_manage.html", {"user": username, "tasks": tasks})



#չʾweb��ʱ�������
@login_required
def appUI_periodic_task(request):
    username = request.session.get('user','')
    tasks = apptest_task.objects.all()
    cases = Appcase.objects.all()
    singel_tasks = apptest_task.objects.get_queryset().order_by('task_id')
    paginator = Paginator(singel_tasks, 15)  # ����paginator����,����ÿҳ��ʾ15����¼
    page = request.GET.get('page', 1)  # ��ȡ��ǰҳΪ��1ҳ
    currentPage = int(page)  # �ѵ�ǰҳת��������
    try:
        singel_tasks = paginator.page(page)  # ��ȡ��ǰҳ�����ļ�¼�б�
    except PageNotAnInteger:
        singel_tasks = paginator.page(1)  # ��������ҳ��������������ʾ��1ҳ����
    except EmptyPage:
        singel_tasks = paginator.page(paginator.num_pages)  # �������ĵ�ҳ������ϵͳ��ҳ���У�����ʾ���һҳ
    return  render(request, "appcase_periodic_task.html", {"user": username, "singel_tasks": singel_tasks,"cases":cases,"tasks": tasks})

#���webUI���Զ�ʱ������ģ̬�����
@login_required
def add_task_appcase_test(request):
    username = request.session.get('user', '')
    tasks = apptest_task.objects.all()
    if request.method == "POST":
        objs = request.POST.get("objstring")
        obj = json.loads(objs)
        for i in range(0, len(obj)):
            id=int(obj[i]['id'])
            appcase_models = obj[i]['appcase_models']
            appcasename = obj[i]['appcasename']
            appcasedesc = obj[i]['appcasedesc']
            apptest_task.objects.create(case_id=id,task_modelname=appcase_models,task_casename=appcasename,task_stepdesc=appcasedesc)
        return  render(request, "appcase_periodic_task.html",{"user": username, "tasks": tasks})


#����ִ�е�ǰ�б��ڵ�����
@login_required
def run_appcase_immediately(request):
    username = request.session.get('user', '')
    tasks = apptest_task.objects.all()
    if request.method == "POST":
        write_name_txt()
        time.sleep(2)
        get_task_stepdata()
        time.sleep(1)
        run_in_terminal()
    return render(request, "appcase_periodic_task.html", {"user": username, "tasks": tasks})



#��ȡǰ�˵Ķ�ʱ����ʱ�䲢���ݸ�task
def get_webcase_task_time(request):
    username = request.session.get('user', '')
    data = {
        'username':username,
        'use':'webcase_periodic_tasktime_get',
    }
    if request.method == "POST":
        singel_task_date = request.POST.get('date')
        get_apptask_times(singel_task_date)
    return HttpResponse(json.dumps(data))