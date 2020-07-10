from django.http import JsonResponse

from .models import teacherData
from utils.tools import listSplit


def addTeacher(requestData):
    if isSuper(requestData['username']):
        teacher = teacherData.objects.filter(user_name=requestData['addForm']['user_name']).count()
        if teacher > 0:
            return JsonResponse({'ret': 1, 'data': '已有同名账户，请重命名！'})
        if teacherData.objects.create(**requestData['addForm']):
            return JsonResponse({'ret': 0, 'data': '新增教师成功！'})


def getTeacherData(requestData):
    """
    获取教师管理列表数据
    :param requestData:
    :return:
    """
    keyWord = requestData['keyWord']  # 查询的关键词
    pageNum = requestData['pageNum']  # 当前页数
    pageSize = requestData['pageSize']  # 一页多少数据

    if isSuper(requestData['username']):
        teachers = list(teacherData.objects.filter(teacher_name__contains=keyWord).values())
    else:
        teachers = []

    myData = listSplit(teachers, pageSize, pageNum)

    return JsonResponse({
        'ret': 0,
        'data': myData['currentData'],
        'pageNum': pageNum,
        'total': len(teachers),
    })


def editTeacher(requestData):
    if isSuper(requestData['username']):
        if teacherData.objects.filter(user_name=requestData['editForm']['user_name']).update(**requestData['editForm']):
            return JsonResponse({'ret': 0, 'data': '教师信息修改成功！'})
        return JsonResponse({'ret': 1, 'data': '教师信息修改失败，请稍后重试！'})


def deleteTeacher(requestData):
    if isSuper(requestData['username']):
        if teacherData.objects.filter(user_name=requestData['teacher']).delete():
            return JsonResponse({'ret': 0, 'data': '教师信息删除成功！'})
        return JsonResponse({'ret': 1, 'data': '教师信息删除失败，请稍后重试！'})


def isSuper(username):
    return list(teacherData.objects.filter(user_name=username).values())[0]['is_super']
