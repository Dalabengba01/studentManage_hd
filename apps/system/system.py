import time

from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import teacherData, systemLogs


# 系统初始化
def systemInit(requestData):
    if int(teacherData.objects.count()) <= 0:
        teacherData.objects.create(user_name=requestData['username'], user_pass=requestData['password'])
        # 使用日志收集
        logs(requestData)
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
    try:
        userList = list(teacherData.objects.filter(user_name=username, user_pass=password).values())[0]
        if (userList['user_name'] == username) and (userList['user_pass'] == password):
            teacherData.objects.filter(user_name=username).update(is_login=True)
            # 使用日志收集
            logs(requestData)
            return JsonResponse({'ret': 0, 'data': '账号登录系统成功！'})
    except Exception:
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


# 用户及系统操作日志收集记录
def logs(data):
    """
    用户及系统操作日志收集记录
    :return:
    """
    # 操作性质API接口字典
    apiName = {
        'userLogout': '用户退出',
        'isSystemInit': '系统是否初始化',
        'systemInit': '系统初始化',
        'userLogin': '用户登陆',
        'userModifyAccount': '用户修改账号名称',
        'userModifyPass': '用户修改账号密码',
        'addProfession': '添加专业',
        'editProfession': '编辑专业信息',
        'deleteProfession': '删除专业',
        'addClasses': '添加班级',
        'editClasses': '编辑班级信息',
        'deleteClasses': '删除班级',
        'addEnterprise': '添加企业',
        'editEnterprise': '编辑企业信息',
        'deleteEnterprise': '删除企业',
        'addPost': '添加岗位',
        'editPost': '编辑岗位信息',
        'deletePost': '删除岗位',
        'addstudent': '添加学生',
        'editStudent': '编辑学生信息',
        'deleteStudent': '删除学生'
    }

    try:
        operationUser = data['username']
    except Exception:
        operationUser = 'system'
    try:
        operationType = apiName[data['useraction']]
        dataRecord = data
        index = 1000
        # 正序查询
        dataList = list(systemLogs.objects.values().order_by('logCode'))
        if len(dataList) <= 0:
            index = 1000
        else:
            index = int(dataList[-1]['logCode']) + 1
        systemLogs.objects.create(logCode=index, operationUser=operationUser, operationType=operationType,
                                  dataRecord=dataRecord)
    except Exception:
        operationType = ''


def getSystemLogsData(requestData):
    """
    获取系统操作日志
    :param requestData:
    :return:
    """
    queryData = requestData['query']  # 查询的元数据
    keyWord = queryData['keyWord']  # 查询的关键词
    pageNum = queryData['pageNum']  # 当前页数
    pageSize = queryData['pageSize']  # 一页多少数据
    queryType = queryData['queryType']  # 搜索类型

    obj = systemLogs.objects
    dataList = []
    if keyWord == '' and queryType == 'noSearch':
        dataList = list(obj.values())

    if keyWord != '' and queryType == 'operationUser':
        dataList = list(obj.filter(operationUser__contains=keyWord).values())

    if keyWord != '' and queryType == 'operationType':
        dataList = list(obj.filter(operationType__contains=keyWord).values())

    paginator = Paginator(dataList, pageSize)  # 每页显示多少数据
    total = paginator.count  # 总数据量
    data = paginator.page(pageNum).object_list  # 某一页的数据

    return JsonResponse({
        'ret': 0,
        'data': data,
        'pageNum': pageNum,
        'total': total,
    })


def deleteSystemLogsData(requestData):
    if systemLogs.objects.filter().delete():
        return JsonResponse({'ret': 0, 'data': '删除系统操作日志成功！'})
    else:
        return JsonResponse({'ret': 1, 'data': '删除系统操作日志失败，请稍后重试！'})
