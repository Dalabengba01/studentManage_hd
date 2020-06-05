from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import professionManage, classesManage, classesBindProfession, studentManage


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
        index = 1000
        # 正序查询
        dataList = list(classesManage.objects.values().order_by('classesCode'))
        if len(dataList) <= 0:
            index = 1000
        else:
            index = int(dataList[-1]['classesCode']) + 1
        if classesManage.objects.create(classesCode=index, classesName=classesName,
                                        classesLevel=requestData['classesLevel']):
            classesCode = list(classesManage.objects.filter(classesName=classesName).values())[0]['classesCode']
            if classesBindProfession.objects.filter(classesCode=classesCode).count() > 0:
                return JsonResponse({'ret': 1, 'data': '已经绑定专业,无需重复绑定!'})
            if classesBindProfession.objects.create(classesCode=classesCode, professionCode=professionCode):
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
    if classesManage.objects.filter(classesCode=classesCode).delete() and classesBindProfession.objects.filter(
            classesCode=classesCode).delete():
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

    # 提取班级人数
    classData = []
    for i in classesManage.objects.values():
        classesHumanNumData = []
        for ii in studentManage.objects.values():
            if str(i['classesCode']) == str(ii['classesCode']):
                classesHumanNumData.append({'classesCode': i['classesCode']})
        classData.append({'classesCode': i['classesCode'], 'classesHumanNumData': classesHumanNumData})

    # 合并到源数据
    classContainer = []
    for i in classesManage.objects.filter(classesName__contains=keyWord).values():
        classesCode = i['classesCode']
        classesLevel = i['classesLevel']
        classesName = i['classesName']
        toProfession = '未绑定'
        for iii in classesBindProfession.objects.filter(classesCode=classesCode).values():
            for iiii in professionManage.objects.filter(professionCode=iii['professionCode']).values():
                toProfession = iiii['professionName']
        toProfession = toProfession
        addTime = i['addTime']
        hh = {'classesCode': classesCode, 'classesLevel': classesLevel, 'classesName': classesName,
              'toProfession': toProfession, 'addTime': addTime}
        for ii in classData:
            if str(i['classesCode']) == str(ii['classesCode']):
                classesHumanNum = len(ii['classesHumanNumData'])
                hh.update({'classesHumanNum': classesHumanNum})
        classContainer.append(hh)

    userList = classContainer

    paginator = Paginator(userList, pageSize)  # 每页显示多少数据
    total = paginator.count  # 总数据量
    # sumPageNum = paginator.num_pages # 总页数
    data = paginator.page(pageNum).object_list  # 某一页的数据

    return JsonResponse({
        'ret': 0,
        'data': data,
        'pageNum': pageNum,
        'total': total,
    })


def getProfessionDataCascaderOptions(requestData):
    """
    获取专业数据供班级页面联动菜单使用
    :param requestData:
    :return:
    """
    data = []
    for i in professionManage.objects.values():
        data.append({'value': i['professionCode'], 'label': i['professionName']})
    return JsonResponse({'ret': 0, 'data': data})


def getProfessionAndClassesLevelDataCascaderOptions(requestData):
    """
    获取专业数据及子菜单(班级)及其对应届数供学生页面联动菜单使用
    :param requestData:
    :return:
    """

    # 合成专业数据
    global classesLevelData
    professionData = []  # 临时存放专业数据
    for i in professionManage.objects.values():
        professionCode = i['professionCode']
        professionName = i['professionName']
        professionData.append({'value': str(professionCode), 'label': professionName, 'disabled': True})

    # 提取绑定关系数据
    bindData = []
    for i in classesBindProfession.objects.values():
        for ii in classesManage.objects.values():
            if i['classesCode'] == ii['classesCode']:
                classesCode = ii['classesCode']
                classesName = ii['classesName']
                classesLevel = ii['classesLevel']
                professionCode = i['professionCode']
                bindData.append(
                    {'value': str(classesCode), 'label': classesName, 'classesLevel': classesLevel,
                     'professionCode': str(professionCode)})

    # 提取班级届数
    classesLevelList = []
    for i in bindData:
        if i['classesLevel'] not in classesLevelList:
            classesLevelList.append(i['classesLevel'])

    # 合成班级数据
    classesData = []
    for i in professionData:
        allClasses = []
        for ii in bindData:
            classesCode = ii['value']
            classesName = ii['label']
            classesLevel = ii['classesLevel']
            if i['value'] == ii['professionCode']:
                allClasses.append(
                    {'professionCode': ii['professionCode'], 'value': str(classesCode), 'label': classesName,
                     'classesLevel': classesLevel})

        # 班级届数分类
        for iii in classesLevelList:
            classes = []
            professionCode = 0
            for iiii in allClasses:
                if iii == iiii['classesLevel']:
                    professionCode = iiii['professionCode']
                    classes.append(iiii)
            classesData.append(
                {'professionCode': professionCode, 'value': iii, 'label': iii, 'children': classes})

    # 合成最终数据
    professionContainer = []  # 专业容器包含班级子容器 value:专业编号 label:专业名称
    for i in professionData:
        professions = []
        for ii in classesData:
            if str(ii['professionCode']) == str(i['value']):
                i['disabled'] = False
                professions.append(ii)
        professionContainer.append(
            {'value': i['value'], 'label': i['label'], 'children': professions, 'disabled': False})

    return JsonResponse({'ret': 0, 'data': professionContainer})


def getProfessionAndClassesDataCascaderOptions(requestData):
    """
    获取专业及包含届数
    :param requestData:
    :return:
    """
    data = []
    for i in list(professionManage.objects.values()):
        professions = []
        for ii in list(classesBindProfession.objects.values()):
            if str(i['professionCode']) == str(ii['professionCode']):
                for iii in list(classesManage.objects.filter(classesCode=ii['classesCode']).values()):
                    if str(iii['classesCode']) == str(ii['classesCode']):
                        if {'value': iii['classesLevel'], 'label': iii['classesLevel']} not in professions:
                            professions.append({'value': iii['classesLevel'], 'label': iii['classesLevel']})
        data.append({'value': i['professionCode'], 'label': i['professionName'], 'disabled': False, 'children': professions})

    return JsonResponse({'ret': 0, 'data': data})