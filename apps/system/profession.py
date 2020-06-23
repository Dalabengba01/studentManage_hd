from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import professionManage, classesManage, \
    studentManage
from utils.tools import getIndex, listSplit


def addProfession(requestData):
    """
    创建专业操作函数
    :param requestData:
    :return:
    """
    if professionManage.objects.filter(professionName=requestData['professionName']).values():
        return JsonResponse({'ret': 1, 'data': '已有相同名称专业,请重命名！'})
    else:
        index = getIndex(professionManage, 'professionCode')
        if professionManage.objects.create(professionCode=index, professionName=requestData['professionName']):
            return JsonResponse({'ret': 0, 'data': '添加专业成功！'})
        else:
            return JsonResponse({'ret': 1, 'data': '添加专业失败,请稍后重试！'})


def editProfession(requestData):
    """
    修改专业名称操作函数
    :param requestData:
    :return:
    """
    professionName = ''
    for i in professionManage.objects.values():
        if i['professionCode'] == requestData['professionCode']:
            professionName = i['professionName']
    if professionManage.objects.filter(professionCode=requestData['professionCode']).update(
            professionName=requestData['professionName']):
        return JsonResponse({'ret': 0, 'data': '修改专业名称成功！'})
    else:
        return JsonResponse({'ret': 1, 'data': '修改专业名称失败,请稍后重试！'})


def deleteProfession(requestData):
    """
    删除专业操作函数
    :param requestData:
    :return:
    """
    professionCode = requestData['professionCode']
    for i in list(classesManage.objects.filter(professionCode=professionCode, isDelete=False).values()):
        classesManage.objects.filter(classesCode=i).update(isDelete=True)
    if professionManage.objects.filter(professionCode=professionCode).update(isDelete=True) or \
            classesManage.objects.filter(professionCode=professionCode).update(isDelete=True):
        studentManage.objects.filter(professionCode=professionCode).update(professionCode='0', classesCode='0')

        return JsonResponse({'ret': 0, 'data': '删除专业成功！'})
    else:
        return JsonResponse({'ret': 1, 'data': '删除专业失败,请稍后重试！'})


def getProfessionData(requestData):
    """
    获取专业管理页面的专业列表数据
    :param requestData:
    :return:
    """
    queryData = requestData['query']  # 查询的元数据
    keyWord = queryData['keyWord']  # 查询的关键词
    pageNum = queryData['pageNum']  # 当前页数
    pageSize = queryData['pageSize']  # 一页多少数据

    professionData = []
    for profession in professionManage.objects.filter(professionName__contains=keyWord, isDelete=False).values():
        professionClassesNum = classesManage.objects.filter(professionCode=profession['professionCode'],  isDelete=False).count()
        professionHumanNum = studentManage.objects.filter(professionCode=profession['professionCode'],  isDelete=False).count()
        profession.update({'professionClassesNum': professionClassesNum, 'professionHumanNum': professionHumanNum})
        professionData.append(profession)
    myData = listSplit(professionData, pageSize, pageNum)

    return JsonResponse({
        'ret': 0,
        'data': myData['currentData'],
        'pageNum': pageNum,
        'total': len(professionData),
    })
