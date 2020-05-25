from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import professionManage, classesManage, classesBindProfession, \
    studentManage, studentBindClassesAndProfession


def addProfession(requestData):
    """
    创建专业操作函数
    :param requestData:
    :return:
    """
    if professionManage.objects.filter(professionName=requestData['professionName']).values():
        return JsonResponse({'ret': 1, 'data': '已有相同名称专业,请重命名！'})
    else:
        if professionManage.objects.create(professionName=requestData['professionName']):
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
    if professionManage.objects.filter(professionCode=professionCode).delete() and \
            classesBindProfession.objects.filter(professionCode=professionCode).delete() and \
            studentBindClassesAndProfession.objects.filter(professionCode=professionCode).delete():
        # 需要重置已绑定专业的班级还有学生
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

    # 分析专业容器绑定哪些班级子容器
    professionData = []  # 专业容器(其中包班级子容器)
    for i in professionManage.objects.filter(professionName__contains=keyWord).values():
        classesData = {}  # 班级子容器,一次外层for循环代表一个专业容器，并把这个子容器加入到父容器
        hh = []  # 班级数据容器(可容纳多个班级)
        for ii in classesBindProfession.objects.values():
            if str(i['professionCode']) == str(ii['professionCode']):
                classesData = {'classesCode': ii['classesCode']}
                hh.append(classesData)
        professionData.append({'professionCode': i['professionCode'], 'classesData': hh})

    professionContainer = []
    for i in professionManage.objects.filter().values():
        classesData = {}
        hh = []
        professionCode = i['professionCode']
        professionName = i['professionName']
        addTime = i['addTime']
        professionClassesNum = 0
        for ii in professionData:
            if str(i['professionCode']) == str(ii['professionCode']):
                professionClassesNum = len(ii['classesData'])
                professionHumanNum = 0
                for iii in ii['classesData']:
                    classesCode = iii['classesCode']
                    professionHumanNum = professionHumanNum + len(
                        studentBindClassesAndProfession.objects.filter(classesCode=classesCode).values())
                classesData = {'professionCode': professionCode, 'professionName': professionName,
                               'professionHumanNum': professionHumanNum, 'professionClassesNum': professionClassesNum,
                               'addTime': addTime}
                hh.append(classesData)
        professionContainer.append(hh)

    userList = []
    for i in professionContainer:
        for ii in i:
            userList.append(ii)

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
