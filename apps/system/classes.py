from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import professionManage, classesManage, studentManage
from utils.tools import getIndex, listSplit


def addClasses(requestData):
    """
    创建班级操作函数
    :param requestData:
    :return:
    """
    professionCode = requestData['bindProfession'][0]
    classesName = requestData['classesName']

    if classesManage.objects.filter(classesName=classesName).values():
        return JsonResponse({'ret': 1, 'data': '已有相同名称班级,请重命名！'})
    else:
        index = getIndex(classesManage, 'classesCode')
        if classesManage.objects.create(classesCode=index, classesName=classesName,
                                        classesLevel=requestData['classesLevel'], professionCode=professionCode):
            return JsonResponse({'ret': 0, 'data': '添加班级成功！'})
        else:
            return JsonResponse({'ret': 1, 'data': '添加班级失败,请稍后重试！'})


def editClasses(requestData):
    """
    修改班级名称操作函数
    :param requestData:
    :return:
    """
    if classesManage.objects.filter(classesCode=requestData['classesCode']).update(
            classesName=requestData['classesName']):
        return JsonResponse({'ret': 0, 'data': '修改班级名称成功！'})
    else:
        return JsonResponse({'ret': 1, 'data': '修改班级名称失败,请稍后重试！'})


def deleteClasses(requestData):
    """
    删除班级操作函数
    :param requestData:
    :return:
    """
    classesCode = requestData['classesCode']
    if classesManage.objects.filter(classesCode=classesCode).update(isDelete=True):
        studentManage.objects.filter(classesCode=classesCode).update(classesCode='0', professionCode='0')
        # 需要重置已绑定专业的班级还有学生
        return JsonResponse({'ret': 0, 'data': '删除班级成功！'})
    else:
        return JsonResponse({'ret': 1, 'data': '删除班级失败,请稍后重试！'})


def getclassesData(requestData):
    """
    获取班级管理页面的专业列表数据
    :param requestData:
    :return:
    """
    queryData = requestData['query']  # 查询的元数据
    keyWord = queryData['keyWord']  # 查询的关键词
    pageNum = queryData['pageNum']  # 当前页数
    pageSize = queryData['pageSize']  # 一页多少数据

    classObj = classesManage.objects
    classesData = []
    classesList = list(classObj.filter(classesName__contains=keyWord, isDelete=False).values())
    myData = listSplit(classesList, pageSize, pageNum)  # 自定义分页(提高系统运行速度)
    for classes in myData['currentData']:
        for profession in professionManage.objects.filter(professionCode=classes['professionCode'],
                                                          isDelete=False).values():
            classes.update({'toProfession': profession['professionName']})
        studentCount = studentManage.objects.filter(classesCode=classes['classesCode'], isDelete=False).count()
        classes.update({'classesHumanNum': studentCount})
        classesData.append(classes)

    return JsonResponse({
        'ret': 0,
        'data': classesData,
        'pageNum': pageNum,
        'total': myData['dataSum'],
    })


def getProfessionDataCascaderOptions(requestData):
    """
    获取专业数据供班级页面联动菜单使用
    :param requestData:
    :return:
    """
    data = []
    for i in professionManage.objects.filter(isDelete=False).values():
        data.append({'value': i['professionCode'], 'label': i['professionName']})
    return JsonResponse({'ret': 0, 'data': data})


def getProfessionAndClassesLevelDataCascaderOptions(requestData):
    """
    获取专业数据及子菜单(班级)及其对应届数供学生页面联动菜单使用
    :param requestData:
    :return:
    """
    data = []
    for profession in professionManage.objects.filter(isDelete=False).values():
        # 最外层专业
        professionList = {'value': profession['professionCode'], 'label': profession['professionName'], 'disabled': True, 'children': []}
        kk = []
        zz = {}
        for level in classesManage.objects.filter(professionCode=profession['professionCode'], isDelete=False).order_by('classesLevel').values():
            # 中间的届数
            levelClasses = [{'value': i['classesCode'], 'label': i['classesName']} for i in classesManage.objects.filter(classesLevel=level['classesLevel'], professionCode=profession['professionCode'], isDelete=False).order_by('classesLevel').values()]
            if len(levelClasses) > 0:
                zz = {'value': level['classesLevel'], 'label': level['classesLevel'] + '届', 'disabled': False, 'children': levelClasses}
            else:
                zz = {'value': level['classesLevel'], 'label': level['classesLevel'] + '届', 'disabled': False, 'children': levelClasses}
            if zz not in kk:
                kk.append(zz)
        professionList.update({'disabled': False, 'children': kk})
        data.append(professionList)

    return JsonResponse({'ret': 0, 'data': data})


def getProfessionAndClassesDataCascaderOptions(requestData):
    """
    获取专业及包含届数
    :param requestData:
    :return:
    """
    data = []
    for profession in professionManage.objects.filter(isDelete=False).values():
        professionList = {'value': profession['professionCode'], 'label': profession['professionName'],
                          'disabled': True, 'children': []}
        classesLevelList = []
        kk = []
        for classes in classesManage.objects.filter(professionCode=profession['professionCode'],
                                                    isDelete=False).order_by('classesLevel').values():
            if classes['classesLevel'] + '届' not in kk:
                kk.append(classes['classesLevel'] + '届')
                classesLevelList.append({'value': classes['classesLevel'], 'label': classes['classesLevel'] + '届'})
        if len(classesLevelList) > 0:
            professionList.update({'disabled': False, 'children': classesLevelList})
        data.append(professionList)
    return JsonResponse({'ret': 0, 'data': data})

