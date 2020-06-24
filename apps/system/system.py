import time
from datetime import datetime

from django.core.paginator import Paginator
from django.http import JsonResponse

from utils.tools import getIndex
from .models import teacherData, systemLogs, editLocked, professionManage, classesManage, enterpriseManage, \
    enterprisePost, studentManage, studentPostTrack


# 系统初始化
def systemInit(requestData):
    if int(teacherData.objects.count()) <= 0:
        teacherData.objects.create(user_name=requestData['username'], user_pass=requestData['password'],
                                   teacher_name=requestData['teachername'])
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
            return JsonResponse({'ret': 0, 'data': '账号已退出系统，请重新登录！'})


# 用户密码修改
def userModifyPass(requestData):
    username = requestData['username']
    oldPassword = requestData['oldPassword']
    password = requestData['password']
    time.sleep(1.5)
    for i in teacherData.objects.filter(user_name=username, user_pass=oldPassword).values():
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

    for i in teacherData.objects.filter(user_name=username).values():
        if i['user_name'] == username:
            if len(list(teacherData.objects.filter(user_name=newusername).values())) <= 0:
                teacherData.objects.filter(user_name=username).update(user_name=newusername)
                return JsonResponse({'ret': 0, 'data': '账户名称修改成功,请重新登录！'})
            else:
                return JsonResponse({'ret': 1, 'data': '系统已存在同名账户，请更换！'})
        else:
            return JsonResponse({'ret': 1, 'data': '原始账号名称错误！'})


# 用户账户修改
def userModifyTeacher(requestData):
    username = requestData['username']
    teachername = requestData['teachername']
    newusername = requestData['newusername']

    for i in list(teacherData.objects.filter(user_name=username).values()):
        if i['teacher_name'] == teachername:
            if len(list(teacherData.objects.filter(teacher_name=newusername).values())) <= 0:
                teacherData.objects.filter(teacher_name=teachername).update(teacher_name=newusername)
                return JsonResponse({'ret': 0, 'data': '教师名称修改成功！'})
            else:
                return JsonResponse({'ret': 1, 'data': '系统已存在同名教师名称，请更换！'})
        else:
            return JsonResponse({'ret': 1, 'data': '原始教师名称错误！'})


# 操作性质API接口字典
apiName = {
    'userLogout': '用户退出',
    'systemInit': '系统初始化',
    'userLogin': '用户登陆',
    'userModifyAccount': '修改账号名称',
    'userModifyPass': '修改账号密码',
    'userModifyTeacher': '修改教师名称',
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
    'deleteStudent': '删除学生',
    'deletePostTrack': '删除岗位追踪数据'
}


# 用户及系统操作日志收集记录
def logs(data):
    """
    用户及系统操作日志收集记录
    :return:
    """
    try:
        operationUser = data['username']
    except Exception:
        operationUser = 'system'
    try:
        operationType = apiName[data['useraction']]
        if operationType == '用户修改账号密码' or operationType == '用户登陆':
            dataRecord = {'useraction': data['useraction'], 'username': data['username']}
        else:
            dataRecord = data
        index = getIndex(systemLogs, 'logCode')
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


def systemEditLocked(requestData):
    """
    编辑类功能实现编辑锁
    :return:
    """
    userAction = requestData['type']
    userName = requestData['username']
    code = requestData['code']
    obj = editLocked.objects
    index = getIndex(editLocked, 'lockedCode')
    # 如果没有此活动且对应的code则创建
    lockeList = list(obj.filter(userAction=userAction, code=code).values())
    if len(lockeList) <= 0:
        obj.create(lockedCode=index, userAction=userAction, userName=userName, code=code)
        return JsonResponse({'ret': 0})
    else:
        # 否则判断时间是否过期
        lockedTime = datetime.strptime(str(lockeList[0]['lockedTime'])[:19], "%Y-%m-%d %H:%M:%S")
        nowTime = datetime.strptime(str(datetime.now())[:19], "%Y-%m-%d %H:%M:%S")
        outTime = int((nowTime - lockedTime).seconds / 60)
        if outTime > 5:
            # 超时的信息可以删除
            obj.filter(userAction=userAction, code=code).delete()
            obj.create(lockedCode=index, userAction=userAction, userName=userName, code=code)
            return JsonResponse({'ret': 0})
        else:
            # 没超时就判断本次请求是不是和本条记录的userName相同,相同则修改过期时间
            data = list(obj.filter(userAction=userAction, userName=userName, code=code).values())
            if len(data) > 0 and userName == data[0]['userName']:
                obj.get(userAction=userAction, userName=userName, code=code).save()
                return JsonResponse({'ret': 0})
            else:
                teacher = list(teacherData.objects.filter(user_name=lockeList[0]['userName']).values())
                return JsonResponse(
                    {'ret': 1, 'status': False, 'data': '此条信息教师 ' + teacher[0]['teacher_name'] + ' 正在编辑，请稍后重试或者与其协商!'})


def systemDataRecovery(requestData):
    recoveryData = requestData['data']
    operationType = recoveryData['operationType']  # 恢复数据类型
    dataRecord = eval(recoveryData['dataRecord'])  # 数据记录
    # typeList = [v for k, v in apiName.items() if '删除' in v] # 获取API有哪些是提供删除
    # ['删除专业', '删除班级', '删除企业', '删除岗位', '删除学生', '删除岗位追踪数据']
    if operationType == '删除专业':
        # 此条数据标记为不删除
        professionManage.objects.filter(professionCode=dataRecord['professionCode']).update(isDelete=False)
        classesManage.objects.filter(professionCode=dataRecord['professionCode']).update(isDelete=False)

    if operationType == '删除班级':
        classesManage.objects.filter(classesCode=dataRecord['classesCode']).update(isDelete=False)
        classesManage.objects.filter(classesCode=dataRecord['classesCode']).update(isDelete=False)

    if operationType == '删除企业':
        enterpriseManage.objects.filter(enterpriseCode=dataRecord['enterpriseCode']).update(isDelete=False)
        enterprisePost.objects.filter(enterpriseCode=dataRecord['enterpriseCode']).update(isDelete=False)

    if operationType == '删除岗位':
        enterprisePost.objects.filter(postCode=dataRecord['postCode']).update(isDelete=False)
        enterprisePost.objects.filter(postCode=dataRecord['postCode']).update(isDelete=False)

    if operationType == '删除学生':
        studentManage.objects.filter(studentCode=dataRecord['studentCode']).update(isDelete=False)

    if operationType == '删除岗位追踪数据':
        studentPostTrack.objects.filter(trackCode=dataRecord['trackCode']).update(isDelete=False)

    # 同时删除此条日志记录
    if systemLogs.objects.filter(logCode=recoveryData['logCode']).delete():
        return JsonResponse({'ret': 0, 'data': '数据恢复成功！'})
    else:
        return JsonResponse({'ret': 0, 'data': '数据恢复失败，请稍后重试！'})


def deleteSystemLogsData(requestData):
    if systemLogs.objects.filter(logCode=requestData['logCode']).delete():
        return JsonResponse({'ret': 0, 'data': '删除操作日志成功！'})
    else:
        return JsonResponse({'ret': 1, 'data': '删除操作日志失败，请稍后重试！'})