from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import professionManage, classesManage, classesBindProfession, \
    studentManage, studentBindClassesAndProfession, employmentReturnVisit
import datetime


def addstudent(requestData):
    """
    创建学生操作函数
    :param requestData:
    :return:
    """
    studentCode = requestData['studentCode']
    studentName = requestData['studentName']
    studentSex = requestData['studentSex']
    studentPhone = requestData['studentPhone']
    employmentStatus = requestData['employmentStatus']
    companyName = requestData['companyName']
    postName = requestData['postName']
    studentSalary = requestData['studentSalary']
    companyPhone = requestData['companyPhone']
    companyAddress = requestData['companyAddress']
    teacherName = requestData['teacherName']
    teacherPhone = requestData['teacherPhone']
    studentStatus = requestData['studentStatus']
    professionCode = requestData['classesAndProfesion'][0]
    classesCode = requestData['classesAndProfesion'][1]
    returnVisit = requestData['returnVisit']

    if studentManage.objects.filter(studentCode=studentCode).values():
        return JsonResponse({'ret': 1, 'data': '已有相同学号,请检查！'})
    else:
        if studentManage.objects.create(studentCode=studentCode, studentName=studentName, studentSex=studentSex,
                                        studentPhone=studentPhone, employmentStatus=employmentStatus,
                                        companyName=companyName, postName=postName, studentSalary=studentSalary,
                                        companyPhone=companyPhone, companyAddress=companyAddress,
                                        teacherName=teacherName, teacherPhone=teacherPhone,
                                        studentStatus=studentStatus) and \
                studentBindClassesAndProfession.objects.create(studentCode=studentCode, professionCode=professionCode,
                                                               classesCode=classesCode):
            index = 1000
            # 正序查询
            dataList = list(employmentReturnVisit.objects.values().order_by('statusID'))
            if len(dataList) <= 0:
                index = 1000
            else:
                index = int(dataList[-1]['statusID']) + 1
            employmentReturnVisit.objects.create(statusID=index, studentCode=studentCode)
            updateReturnVisit(studentCode, returnVisit)

            return JsonResponse({'ret': 0, 'data': '创建学生成功!'})
        else:
            return JsonResponse({'ret': 1, 'data': '创建学生失败,请稍后重试!'})


def deleteStudent(requestData):
    """
    删除学生操作
    :param requestData:
    :return:
    """
    studentCode = requestData['studentCode']
    if studentManage.objects.filter(studentCode=studentCode).delete() and \
            studentBindClassesAndProfession.objects.filter(studentCode=studentCode).delete() and \
            employmentReturnVisit.objects.filter(studentCode=studentCode).delete():
        return JsonResponse({'ret': 0, 'data': '删除学生信息成功!'})
    else:
        return JsonResponse({'ret': 1, 'data': '删除学生信息失败,请稍后重试!'})


def getEmploymentStatusData(requestData):
    """
    获取学生就业状态详细数据操作函数
    :param requestData:
    :return:
    """
    queryData = requestData['query']  # 查询的元数据
    keyWord = queryData['keyWord']  # 查询的关键词
    pageNum = queryData['pageNum']  # 当前页数
    pageSize = queryData['pageSize']  # 一页多少数据
    queryType = queryData['queryType']  # 搜索类型

    subData0 = []
    if queryType is None or queryType == '' or \
            queryType == 'studentName' or \
            queryType == 'professionName' or \
            queryType == 'classesName':
        for i in list(employmentReturnVisit.objects.filter().values()):
            subData0.append(i)

    if queryType == 'studentCode':
        for i in list(employmentReturnVisit.objects.filter(studentCode__contains=keyWord).values()):
            subData0.append(i)

    # 最终数据列表合成
    userList = []
    for i in subData0:
        studentCode = i['studentCode']
        studentName = ''
        toProfession = ''
        toClasses = ''

        # 获取专业名称和班级名称
        for ii in studentBindClassesAndProfession.objects.filter(studentCode=studentCode).values():
            professionCode = ii['professionCode']
            classesCode = ii['classesCode']
            for iii in professionManage.objects.filter(professionCode=professionCode).values():
                toProfession = iii['professionName']
            for iiii in classesManage.objects.filter(classesCode=classesCode).values():
                toClasses = iiii['classesName']

        # 获取学生名称
        for iiiii in studentManage.objects.filter(studentCode=studentCode).values():
            studentName = iiiii['studentName']
        data = {}
        data.update({'studentName': studentName, 'toProfession': toProfession, 'toClasses': toClasses})
        data.update(i)
        # 合成最终数据
        userList.append(data)

    # 用户按照姓名查找
    queryTypeStudentName = []
    if queryType == 'studentName':
        for i in userList:
            if i['studentName'].find(keyWord) != -1:
                queryTypeStudentName.append(i)
        userList = queryTypeStudentName

    # 用户按照专业名查找
    queryTypeProfessionName = []
    if queryType == 'professionName':
        for i in userList:
            if i['toProfession'].find(keyWord) != -1:
                queryTypeProfessionName.append(i)
        userList = queryTypeProfessionName

    # 用户按照班级名查找
    queryTypeClassesName = []
    if queryType == 'classesName':
        for i in userList:
            if i['toClasses'].find(keyWord) != -1:
                queryTypeClassesName.append(i)
        userList = queryTypeClassesName

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


def editStudent(requestData):
    """
    修改学生信息操作
    :param requestData:
    :return:
    """
    studentCode = requestData['studentCode']
    studentName = requestData['studentName']
    studentSex = requestData['studentSex']
    studentPhone = requestData['studentPhone']
    employmentStatus = requestData['employmentStatus']
    companyName = requestData['companyName']
    companyAddress = requestData['companyAddress']
    postName = requestData['postName']
    studentSalary = requestData['studentSalary']
    companyPhone = requestData['companyPhone']
    teacherName = requestData['teacherName']
    teacherPhone = requestData['teacherPhone']
    studentStatus = requestData['studentStatus']
    professionCode = requestData['classesAndProfesion'][0]
    classesCode = requestData['classesAndProfesion'][1]
    returnVisit = requestData['returnVisit']

    if studentBindClassesAndProfession.objects.filter(studentCode=studentCode).values():
        if studentManage.objects \
                .filter(studentCode=studentCode) \
                .update(studentCode=studentCode,
                        studentName=studentName, studentSex=studentSex,
                        studentPhone=studentPhone,
                        employmentStatus=employmentStatus,
                        companyName=companyName,
                        companyAddress=companyAddress,
                        postName=postName,
                        studentSalary=studentSalary,
                        companyPhone=companyPhone,
                        teacherName=teacherName,
                        teacherPhone=teacherPhone,
                        studentStatus=studentStatus) and \
                studentBindClassesAndProfession.objects.filter(studentCode=studentCode).update(
                    professionCode=professionCode, classesCode=classesCode):
            # 更新回访数据
            updateReturnVisit(studentCode, returnVisit)

            return JsonResponse({'ret': 0, 'data': '修改基本信息成功!'})
        else:
            return JsonResponse({'ret': 1, 'data': '修改基本信息失败,请稍后重试!'})
    else:
        studentBindClassesAndProfession.objects.create(studentCode=studentCode, professionCode=professionCode,
                                                       classesCode=classesCode)
        studentManage.objects.filter(studentCode=studentCode).update(studentName=studentName)
        return JsonResponse({'ret': 0, 'data': '修改基本信息成功!'})


def getStudentData(requestData):
    """
    获取学生信息操作函数
    :param requestData:
    :return:学生数据
    """
    queryData = requestData['query']  # 查询的元数据
    keyWord = queryData['keyWord']  # 查询的关键词
    pageNum = queryData['pageNum']  # 当前页数
    pageSize = queryData['pageSize']  # 一页多少数据
    queryType = queryData['queryType']  # 搜索类型
    searchType = queryData['searchType']  # 显示数据类型(默认全部数据)

    # 创建新的列表供后续功能操作
    subData0 = []

    if queryType == 'noSearch' and keyWord == '' and searchType in ['全部', '参军', '待安置', '已安置', '拟升学']:

        if searchType == '全部':
            subData0 = list(studentManage.objects.filter().values())

        if searchType == '参军':
            subData0 = list(studentManage.objects.filter(employmentStatus='参军').values())

        if searchType == '待安置':
            subData0 = list(studentManage.objects.filter(employmentStatus='待安置').values())

        if searchType == '已安置':
            subData0 = list(studentManage.objects.filter(employmentStatus='已安置').values())

        if searchType == '拟升学':
            subData0 = list(studentManage.objects.filter(employmentStatus='拟升学').values())

    if queryType == 'studentCode' and keyWord != '':
        subData0 = list(studentManage.objects.filter(studentCode__contains=keyWord).values())

    if queryType == 'studentName' and keyWord != '':
        subData0 = list(studentManage.objects.filter(studentName__contains=keyWord).values())

    # 获取所属专业,班级名称，班级届数并合并到学生信息列表中
    userList = []
    for i in subData0:
        if studentBindClassesAndProfession.objects.filter(studentCode=i['studentCode']).count() > 0:
            for ii in studentBindClassesAndProfession.objects.filter(studentCode=i['studentCode']).values():
                studentLevel = ''
                toClasses = ''
                toProfession = ''
                for iii in classesManage.objects.filter(classesCode=ii['classesCode']).values():
                    studentLevel = iii['classesLevel']
                    toClasses = iii['classesName']
                for iiii in professionManage.objects.filter(professionCode=ii['professionCode']).values():
                    toProfession = iiii['professionName']
                i.update({'studentLevel': studentLevel, 'toProfession': toProfession, 'toClasses': toClasses})
        else:
            i.update({'studentLevel': '未绑定', 'toProfession': '未绑定', 'toClasses': '未绑定'})
        userList.append(i)
    paginator = Paginator(userList, pageSize)  # 每页显示多少数据
    total = paginator.count  # 总数据量
    data = paginator.page(pageNum).object_list  # 某一页的数据

    return JsonResponse({
        'ret': 0,
        'data': data,
        'pageNum': pageNum,
        'total': total,
    })


def returnVisitData(requestData):
    """
    获取学生回访信息
    :param requestData:
    :return:
    """
    studentCode = requestData['studentCode']
    data = list(employmentReturnVisit.objects.filter(studentCode=studentCode).values())
    if data:
        return JsonResponse({'ret': 0, 'data': data})
    else:
        return JsonResponse({'ret': 1, 'data': '获取数据失败！'})


def getProfessionAndClassesDataCascaderOptions(requestData):
    """
    获取专业数据及子菜单(班级)供学生页面联动菜单使用
    :param requestData:
    :return:
    """
    test = [
        {'value': '1', 'label': '云计算与技术',
         'children': [
             {'value': '11', 'label': '云算3182'},
             {'value': '12', 'label': '云算3181'}
         ]},
        {'value': '2', 'label': '移动通信技术',
         'children': [
             {'value': '1233', 'label': '移动3192'},
             {'value': 'da', 'label': '移动321'}
         ]}
    ]

    # 合成专业数据
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
                professionCode = i['professionCode']
                bindData.append(
                    {'value': str(classesCode), 'label': classesName, 'professionCode': str(professionCode)})

    # # 合成班级数据
    classesData = []
    for i in professionData:
        childrenData = []
        for ii in bindData:
            classesCode = ii['value']
            classesName = ii['label']
            if i['value'] == ii['professionCode']:
                childrenData.append({'value': str(classesCode), 'label': classesName})
        classesData.append({'professionCode': i['value'], 'children': childrenData})
    # print(classesData)

    # 合成最终数据
    professionContainer = []  # 专业容器包含班级子容器 value:专业编号 label:专业名称
    for i in professionData:
        for ii in bindData:
            if i['value'] == ii['professionCode']:
                # classesContainer = []  # 班级要嵌套到专业父容器中 value: 班级编号 label: 班级名称
                i['disabled'] = False
                for iii in classesData:
                    if iii['professionCode'] == ii['professionCode']:
                        i.update({'children': iii['children']})
        professionContainer.append(i)

    # print(bindData)
    # print(professionContainer)
    return JsonResponse({'ret': 0, 'data': professionContainer})


def updateReturnVisit(studentCode, returnVisit):
    """
    更新回访数据
    :return:
    """
    month = datetime.datetime.now().month
    obj = employmentReturnVisit.objects.filter(studentCode=studentCode)
    if month == 1:
        obj.update(data1=returnVisit)
    if month == 2:
        obj.update(data2=returnVisit)
    if month == 3:
        obj.update(data3=returnVisit)
    if month == 4:
        obj.update(data4=returnVisit)
    if month == 5:
        obj.update(data5=returnVisit)
    if month == 6:
        obj.update(data6=returnVisit)
    if month == 7:
        obj.update(data7=returnVisit)
    if month == 8:
        obj.update(data8=returnVisit)
    if month == 9:
        obj.update(data9=returnVisit)
    if month == 10:
        obj.update(data10=returnVisit)
    if month == 11:
        obj.update(data11=returnVisit)
    if month == 12:
        obj.update(data12=returnVisit)
