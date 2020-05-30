from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import professionManage, classesManage, classesBindProfession, \
    studentManage, enterprisePost, enterpriseManage
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
    studentNativePlace = requestData['studentNativePlace']
    studentPhone = requestData['studentPhone']
    employmentStatus = requestData['employmentStatus']
    studentSalary = requestData['studentSalary']
    teacherName = requestData['teacherName']
    teacherPhone = requestData['teacherPhone']
    studentStatus = requestData['studentStatus']
    professionCode = requestData['classesAndProfesion'][0]
    classesCode = requestData['classesAndProfesion'][1]
    postDuty = requestData['postDuty']
    try:
        enterpriseCode = requestData['enterpriseAndPostData'][0]
        postCode = requestData['enterpriseAndPostData'][1]
    except Exception:
        enterpriseCode = 0
        postCode = 0

    if studentManage.objects.filter(studentCode=studentCode).values():
        return JsonResponse({'ret': 1, 'data': '已有相同学号,请检查！'})
    else:
        if studentManage.objects.create(studentCode=studentCode, studentName=studentName, studentSex=studentSex,
                                        studentNativePlace=studentNativePlace,
                                        studentPhone=studentPhone, employmentStatus=employmentStatus,
                                        studentSalary=studentSalary,
                                        teacherName=teacherName, teacherPhone=teacherPhone,
                                        studentStatus=studentStatus, professionCode=professionCode,
                                        classesCode=classesCode, enterpriseCode=enterpriseCode,
                                        postCode=postCode, postDuty=postDuty):
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
    if studentManage.objects.filter(studentCode=studentCode).delete():
        return JsonResponse({'ret': 0, 'data': '删除学生信息成功!'})
    else:
        return JsonResponse({'ret': 1, 'data': '删除学生信息失败,请稍后重试!'})


def editStudent(requestData):
    """
    修改学生信息操作
    :param requestData:
    :return:
    """
    studentCode = requestData['studentCode']
    studentName = requestData['studentName']
    studentSex = requestData['studentSex']
    studentNativePlace = requestData['studentNativePlace']
    studentPhone = requestData['studentPhone']
    studentStatus = requestData['studentStatus']
    teacherName = requestData['teacherName']
    teacherPhone = requestData['teacherPhone']
    employmentStatus = requestData['employmentStatus']
    studentSalary = requestData['studentSalary']
    postDuty = requestData['postDuty']

    try:
        professionCode = requestData['classesAndProfesion'][0]
        classesCode = requestData['classesAndProfesion'][1]
    except Exception:
        professionCode = '0'
        classesCode = '0'
    try:
        enterpriseCode = requestData['enterpriseAndPostData'][0]
        postCode = requestData['enterpriseAndPostData'][1]
    except Exception:
        enterpriseCode = '0'
        postCode = '0'

    if studentManage.objects \
            .filter(studentCode=studentCode) \
            .update(studentName=studentName, studentSex=studentSex, studentNativePlace=studentNativePlace,
                    professionCode=professionCode,
                    classesCode=classesCode, studentPhone=studentPhone, studentStatus=studentStatus,
                    teacherName=teacherName, teacherPhone=teacherPhone, employmentStatus=employmentStatus,
                    studentSalary=studentSalary, enterpriseCode=enterpriseCode, postCode=postCode, postDuty=postDuty):

        return JsonResponse({'ret': 0, 'data': '修改基本信息成功!'})
    else:
        return JsonResponse({'ret': 1, 'data': '修改基本信息失败,请稍后重试!'})


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

    if queryType == 'classesName' and keyWord != '':
        # 1.查询此班级的编号
        classesCode = str(list(classesManage.objects.filter(classesName__contains=keyWord).values())[0]['classesCode'])
        # 2.利用此编号查询学生绑定班级专业表
        bindCode = list(studentManage.objects.filter(classesCode=classesCode).values())
        # 3.存储有此班级编号的学号
        studentCodeList = [str(i['studentCode']) for i in bindCode if str(i['classesCode']) == str(classesCode)]
        studentData = []
        for i in studentCodeList:
            studentData.append(list(studentManage.objects.filter(studentCode=i).values())[0])
        subData0 = studentData

    userList = []
    for i in subData0:
        # 获取所属专业,班级名称，班级届数并合并到学生信息列表中
        for ii in studentManage.objects.filter(studentCode=i['studentCode']).values():
            if ii['classesCode'] != '0':
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

        # 获取岗位信息和企业信息
        for studentBindData in list(studentManage.objects.filter(studentCode=i['studentCode']).values()):
            if studentBindData['postCode'] != '0':
                for postData in list(enterprisePost.objects.filter(postCode=studentBindData['postCode']).values()):
                    i.update(postData)
            else:
                i.update({'postName': '未绑定'})

            if studentBindData['enterpriseCode'] != '0':
                for enterpriseData in list(
                        enterpriseManage.objects.filter(enterpriseCode=studentBindData['enterpriseCode']).values()):
                    i.update(enterpriseData)
            else:
                i.update({'enterpriseName': '未绑定', 'postAddress': '未绑定', 'enterprisePhone': '未绑定'})
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


def getProfessionAndClassesDataCascaderOptions(requestData):
    """
    获取专业数据及子菜单(班级)供学生页面联动菜单使用
    :param requestData:
    :return:
    """

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

    return JsonResponse({'ret': 0, 'data': professionContainer})
