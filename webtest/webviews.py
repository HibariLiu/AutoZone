from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import auth
from django.contrib import messages
from django.core.paginator import  Paginator, EmptyPage, PageNotAnInteger
from webtest.models import Webcasestep,Webcase,Webcase_keywords,webtest_task
from django.core.paginator import  Paginator, EmptyPage, PageNotAnInteger
import os
import pyautogui
from webtest.tasks import write_name_txt,readSQLCounts,get_task_stepdata,getcasename_from_SQL,get_webtask_times
import time
from  webtest.get_webcase_stepdata import readwebcaseSQL,write_to_txt,remove_webtest_txt,run_in_terminal

#显示web测试用例界面
@login_required
def web_testcase_page(request):
    username = request.session.get('user', '')
    webcases = Webcase.objects.get_queryset().order_by('id')
    paginator = Paginator(webcases, 12)  # 生成paginator对象,设置每页显示15条记录
    page = request.GET.get('page', 1)  # 获取当前页为第1页
    currentPage = int(page)  # 把当前页转换成整数
    try:
        webcases = paginator.page(page)  # 获取当前页码数的记录列表
    except PageNotAnInteger:
        webcases = paginator.page(1)  # 如果输入的页数不是整数则显示第1页内容
    except EmptyPage:
        webcases = paginator.page(paginator.num_pages)  # 如果输入的的页数不在系统的页数中，则显示最后一页
    return render(request, "Web_test_robotframework.html", {"user": username, "webcases": webcases})



# #web测试用例名称添加
@login_required
def add_web_casename(request):
    username = request.session.get('user', '')
    webcases = Webcase.objects.all()
    if request.method == "POST":
        webmodelname = request.POST.get("webmodelname", )
        webcasename = request.POST.get("webcasename", )
        webcharger = request.POST.get("webcharger", )
        webaddcasedesc = request.POST.get("webaddcasedesc", )
        Webcase.objects.get_or_create(webcase_models=webmodelname,webcasename=webcasename,webcase_charger=webcharger,webcasedesc=webaddcasedesc)
        return render(request, "Web_test_robotframework.html", {"user": username, "webcases":webcases})


#删除web测试用例
@login_required
def del_web_casename(request):
    username = request.session.get('user', '')
    webcases = Webcase.objects.all()
    if request.method == "POST":
        webcaseID = request.POST.get("id", )
        Webcase.objects.filter(id=webcaseID).delete()
        return render(request, "Web_test_robotframework.html", {"user": username, "webcases":webcases})


#显示web测试步骤添加
@login_required
def display_web_casesteps(request):
    username = request.session.get('user', '')
    webcaseid = request.GET.get('webcase.id',None)
    webcase = Webcase.objects.get(id=webcaseid)
    webcasesteps = Webcasestep.objects.all()
    return render(request,"webcasestep_manage.html",{"user": username,"webcasesteps":webcasesteps,"webcase":webcase})


#删除web测试步骤
@login_required
def delete_web_casesteps(request):
    webcaseid = request.POST.get("casename_id")
    username = request.session.get('user', '')
    webcase = Webcase.objects.get(id=webcaseid)
    webcasesteps = Webcasestep.objects.all()
    stepid = request.POST.get("step_id")
    Webcasestep.objects.filter(Webcase_id=webcaseid,id=stepid).delete()
    return render(request, "webcasestep_manage.html",{"user": username, "webcasesteps": webcasesteps, "webcase": webcase})


#上传图片
@login_required
def upload_file(request):
    # 请求方法为POST时，进行处理
    if request.method == "POST":
        # 获取上传的文件，如果没有文件，则默认为None
        File = request.FILES.get("myfile", None)
        if File is None:
            return HttpResponse("没有需要上传的文件")
        else:
            #打开特定的文件进行二进制的写操作
            #print(os.path.exists('/temp_file/'))
            with open("./webtest/media/%s" % File.name, 'wb+') as f:
                #分块写入文件
                for chunk in  File.chunks():
                    f.write(chunk)
            return HttpResponse("UPload over!")
    else:
        return  render(request, "test.html")


#立即执行测试用例
@login_required
def maoyan_test(request):
    username = request.session.get('user', '')
    tasks = Webcasestep.objects.all()
    if request.method == "POST":
        upperlevel_id = request.POST.get("casename_id")
        write_to_txt(upperlevel_id)
        time.sleep(1)
        readwebcaseSQL(upperlevel_id)
    return render(request, "webcasestep_manage.html",{"user": username, "tasks": tasks})

#用例执行成功后保存
@login_required
def remove_test_txt(request):
    username = request.session.get('user', '')
    tasks = Webcasestep.objects.all()
    if request.method =="POST":
        txtname = request.POST.get("casename_id")
        remove_webtest_txt(txtname)
    return render(request, "webcasestep_manage.html", {"user": username, "tasks": tasks})

#------------------------------------------------------------------------------------------------------------------------
#显示关键字以及使用说明
@login_required
def display_keywords(request):
    username = request.session.get('user', '')
    keywords = Webcase_keywords.objects.get_queryset().order_by('keyword_id')
    paginator = Paginator(keywords, 11)  # 生成paginator对象,设置每页显示15条记录
    page = request.GET.get('page', 1)  # 获取当前页为第1页
    currentPage = int(page)  # 把当前页转换成整数
    try:
        keywords = paginator.page(page)  # 获取当前页码数的记录列表
    except PageNotAnInteger:
        keywords = paginator.page(1)  # 如果输入的页数不是整数则显示第1页内容
    except EmptyPage:
        keywords = paginator.page(paginator.num_pages)  # 如果输入的的页数不在系统的页数中，则显示最后一页
    return render(request, "keywordslibrary.html", {"user": username, "keywords": keywords})


#添加关键字
@login_required
def add_keywords(request):
    username = request.session.get('user', '')
    keywords = Webcase_keywords.objects.all()
    if request.method == "POST":
        library = request.POST.get("library", )
        keyword = request.POST.get("keyword", )
        parames = request.POST.get("parames", )
        comment = request.POST.get("comment", )
        Webcase_keywords.objects.get_or_create(library=library, keyword=keyword,parameter=parames,comment=comment)
    return render(request,"keywordslibrary.html",{"user": username, "keywords": keywords})

#删除关键字
@login_required
def del_keywords(request):
    username = request.session.get('user', '')
    keywords = Webcase_keywords.objects.all()
    if request.method == "POST":
        try:
            id= request.POST.get("id")
            print(id)
            Webcase_keywords.objects.filter(keyword_id=id).delete()
        except Exception as e:
            print("error")
    return render(request, "keywordslibrary.html", {"user": username, "keywords": keywords})
#修改关键字参数
@login_required
def change_keywords(request):
    username = request.session.get('user', '')
    keywords = Webcase_keywords.objects.all()
    if request.method == "POST":
        id = request.POST.get("id", )
        library = request.POST.get("library", )
        keyword = request.POST.get("keyword", )
        parames = request.POST.get("addparames", )
        comment = request.POST.get("addcomment", )
        Webcase_keywords.objects.filter(keyword_id=id).update(library=library,keyword=keyword,parameter=parames,comment=comment)
    return render(request, "keywordslibrary.html", {"user": username, "keywords": keywords})



#展示web定时任务界面
@login_required
def webUI_periodic_task(request):
    username = request.session.get('user','')
    tasks = webtest_task.objects.all()
    cases = Webcase.objects.all()
    singel_tasks = webtest_task.objects.get_queryset().order_by('task_id')
    paginator = Paginator(singel_tasks, 15)  # 生成paginator对象,设置每页显示15条记录
    page = request.GET.get('page', 1)  # 获取当前页为第1页
    currentPage = int(page)  # 把当前页转换成整数
    try:
        singel_tasks = paginator.page(page)  # 获取当前页码数的记录列表
    except PageNotAnInteger:
        singel_tasks = paginator.page(1)  # 如果输入的页数不是整数则显示第1页内容
    except EmptyPage:
        singel_tasks = paginator.page(paginator.num_pages)  # 如果输入的的页数不在系统的页数中，则显示最后一页
    return  render(request, "webcase_periodic_task.html", {"user": username, "singel_tasks": singel_tasks,"cases":cases,"tasks": tasks})

#添加webUI测试定时任务在模态框汇总
@login_required
def add_task_webcase_test(request):
    username = request.session.get('user', '')
    tasks = webtest_task.objects.all()
    if request.method == "POST":
        objs = request.POST.get("objstring")
        obj = json.loads(objs)
        for i in range(0, len(obj)):
            id=int(obj[i]['id'])
            webcase_models = obj[i]['webcase_models']
            webcasename = obj[i]['webcasename']
            webcasedesc = obj[i]['webcasedesc']
            webtest_task.objects.create(case_id=id,task_modelname=webcase_models,task_casename=webcasename,task_stepdesc=webcasedesc)
        return  render(request, "webcase_periodic_task.html",{"user": username, "tasks": tasks})


#立即执行当前列表内的任务
@login_required
def run_webcase_immediately(request):
    username = request.session.get('user', '')
    tasks = webtest_task.objects.all()
    if request.method == "POST":
        write_name_txt()
        time.sleep(2)
        get_task_stepdata()
        time.sleep(1)
        run_in_terminal()
    return render(request, "webcase_periodic_task.html", {"user": username, "tasks": tasks})



#获取前端的定时任务时间并传递给task
def get_webcase_task_time(request):
    username = request.session.get('user', '')
    data = {
        'username':username,
        'use':'webcase_periodic_tasktime_get',
    }
    if request.method == "POST":
        singel_task_date = request.POST.get('date')
        get_webtask_times(singel_task_date)
    return HttpResponse(json.dumps(data))