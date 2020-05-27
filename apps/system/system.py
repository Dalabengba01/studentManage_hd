import time
from django.http import JsonResponse
from .models import teacherData


# 系统初始化
def systemInit(requestData):
    if int(teacherData.objects.count()) <= 0:
        teacherData.objects.create(user_name=requestData['username'], user_pass=requestData['password'])
        return JsonResponse({'ret': 0, 'data': '系统初始化成功！'})
    elif int(teacherData.objects.count()) > 0:
        return JsonResponse({'ret': 1, 'data': '系统已经初始化！'})
    else:
        return JsonResponse({'ret': 2, 'data': '系统初始化失败,请稍后重试！'})


# 系统是否初始化
def isSystemInit(requestData):
    if int(teacherData.objects.count()) > 0:
        return JsonResponse({'ret': 0, 'data': '系统已经初始化！'})
    else:
        return JsonResponse({'ret': 1, 'data': '请补充下列管理员信息作为系统初始化数据'})


# 用户登录
def userLogin(requestData):
    username = requestData['username']
    password = requestData['password']
    userList = list(teacherData.objects.values())
    for i in userList:
        if (i['user_name'] == username) and (i['user_pass'] == password):
            teacherData.objects.filter(user_name=username).update(is_login=True)
            return JsonResponse({'ret': 0, 'data': '账号登录系统成功！'})
        else:
            return JsonResponse({'ret': 1, 'data': '账号或密码错误！'})


# 用户登出
def userLogout(requestData):
    username = requestData['username']
    userList = list(teacherData.objects.values())
    for i in userList:
        if i['user_name'] == username:
            teacherData.objects.filter(user_name=username).update(is_login=False)
            return JsonResponse({'ret': 0, 'data': '账号已退出系统登录！'})


# 用户密码修改
def userModifyPass(requestData):
    username = requestData['username']
    oldPassword = requestData['oldPassword']
    password = requestData['password']
    time.sleep(1.5)
    for i in teacherData.objects.values():
        if i['user_name'] == username and i['user_pass'] == oldPassword:
            teacherData.objects.filter(user_name=username).update(user_pass=password)
            return JsonResponse({'ret': 0, 'data': '密码修改成功,请重新登录！'})
        else:
            return JsonResponse({'ret': 1, 'data': '原始密码错误！'})


# 用户账户修改
def userModifyAccount(requestData):
    username = requestData['username']
    newusername = requestData['newusername']
    time.sleep(1.5)
    for i in teacherData.objects.filter().values():
        if i['user_name'] == username:
            teacherData.objects.filter(user_name=username).update(user_name=newusername)
            return JsonResponse({'ret': 0, 'data': '账户名称修改成功,请重新登录！'})
        else:
            return JsonResponse({'ret': 1, 'data': '原始账号名称错误！'})


