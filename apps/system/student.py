from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import professionManage, classesManage, \
    studentManage, enterprisePost, enterpriseManage, studentPostTrack, teacherData
from utils.tools import getIndex, listSplit


def addstudent(requestData):
    """
    创建学生操作函数
    :param requestData:
    :return:
    """
    userName = requestData['username']
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
    remarks = requestData['remarks']
    try:
        enterpriseCode = requestData['enterpriseAndPostData'][0]
        postCode = requestData['enterpriseAndPostData'][1]
    except Exception:
        enterpriseCode = 0
        postCode = 0

    # 检查学生数据是否改变，没有改变则不添加新的岗位追踪数据
    student = list(studentManage.objects.filter(studentCode=studentCode, studentName=studentName,
                                                enterpriseCode=enterpriseCode, postCode=postCode, postDuty=postDuty,
                                                remarks=remarks).values())
    isCreate = False
    if len(student) <= 0:
        isCreate = True

    # 获取企业名称
    enterprise = list(enterpriseManage.objects.filter(enterpriseCode=enterpriseCode).values())
    enterpriseName = ''
    if len(enterprise) > 0:
        enterpriseName = enterprise[0]['enterpriseName']
    # 获取岗位名称
    post = list(enterprisePost.objects.filter(postCode=postCode).values())
    postName = ''
    if len(enterprise) > 0:
        postName = post[0]['postName']

    # 如果数据不存在
    if len(list(studentPostTrack.objects.filter(studentCode=studentCode, studentName=studentName,
                                                studentSalary=studentSalary,
                                                enterpriseName=enterpriseName,
                                                postDuty=postDuty,
                                                remarks=remarks,
                                                postName=postName).values())) <= 0:
        isCreate = True
    else:
        # 如果存在用日期排序获取最后一个查看是否有不同
        postTrack = list(
            studentPostTrack.objects.filter(studentCode=studentCode, studentName=studentName).values().order_by(
                'addTime'))
        if len(postTrack) > 0:
            if studentSalary != postTrack[-1]['studentSalary'] or enterpriseName != postTrack[-1][
                'enterpriseName'] or postDuty != postTrack[-1]['postDuty'] or \
                    remarks != postTrack[-1]['remarks'] or postName != postTrack[-1]['postName']:
                isCreate = True
    # 判断是否创建或更新学生岗位追踪表
    if employmentStatus == '已安置' and isCreate:
        # 1.检查是否存在该学生的变化信息
        teacher = list(teacherData.objects.filter(user_name=requestData['username']).values())
        recordTeacher = ''
        if len(teacher) > 0:
            recordTeacher = teacher[0]['teacher_name']
        index = getIndex(studentPostTrack, 'trackCode')
        studentPostTrack.objects.create(trackCode=index, studentCode=studentCode, studentName=studentName,
                                        studentSalary=studentSalary,
                                        recordTeacher=recordTeacher,
                                        enterpriseName=enterpriseName, postName=postName, postDuty=postDuty,
                                        remarks=remarks)

    if studentManage.objects.filter(studentCode=studentCode).values():
        return JsonResponse({'ret': 1, 'data': '已有相同学号,请检查！'})
    else:
        updateTeacherName = teacherData.objects.filter(user_name=userName).values()[0]['teacher_name']
        if studentManage.objects.create(studentCode=studentCode, studentName=studentName, studentSex=studentSex,
                                        studentNativePlace=studentNativePlace,
                                        studentPhone=studentPhone, employmentStatus=employmentStatus,
                                        studentSalary=studentSalary,
                                        teacherName=teacherName, teacherPhone=teacherPhone, updateTeacherName=updateTeacherName,
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
    if studentManage.objects.filter(studentCode=studentCode).update(isDelete=True):
        return JsonResponse({'ret': 0, 'data': '删除学生信息成功!'})
    else:
        return JsonResponse({'ret': 1, 'data': '删除学生信息失败,请稍后重试!'})


def editStudent(requestData):
    """
    修改学生信息操作
    :param requestData:
    :return:
    """
    userName = requestData['username']
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
    remarks = requestData['remarks']

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

    # 检查学生数据是否改变，没有改变则不添加新的岗位追踪数据
    student = list(studentManage.objects.filter(studentCode=studentCode, studentName=studentName,
                                                enterpriseCode=enterpriseCode, postCode=postCode, postDuty=postDuty,
                                                remarks=remarks).values())
    isCreate = False
    if len(student) <= 0:
        isCreate = True

    # 获取企业名称
    enterprise = list(enterpriseManage.objects.filter(enterpriseCode=enterpriseCode).values())
    enterpriseName = ''
    if len(enterprise) > 0:
        enterpriseName = enterprise[0]['enterpriseName']
    # 获取岗位名称
    post = list(enterprisePost.objects.filter(postCode=postCode).values())
    postName = ''
    if len(enterprise) > 0:
        postName = post[0]['postName']
    # 如果数据不存在
    if len(list(studentPostTrack.objects.filter(studentCode=studentCode, studentName=studentName,
                                                studentSalary=studentSalary,
                                                enterpriseName=enterpriseName,
                                                postDuty=postDuty,
                                                remarks=remarks,
                                                postName=postName).values())) <= 0:
        isCreate = True
    else:
        # 如果存在用日期排序获取最后一个查看是否有不同
        postTrack = list(
            studentPostTrack.objects.filter(studentCode=studentCode, studentName=studentName).values().order_by(
                'addTime'))
        if len(postTrack) > 0:
            if studentSalary != postTrack[-1]['studentSalary'] or enterpriseName != postTrack[-1][
                'enterpriseName'] or postDuty != postTrack[-1]['postDuty'] or \
                    remarks != postTrack[-1]['remarks'] or postName != postTrack[-1]['postName']:
                isCreate = True
    # 判断是否创建或更新学生岗位追踪表
    if employmentStatus == '已安置' and isCreate:
        # 1.检查是否存在该学生的变化信息
        index = getIndex(studentPostTrack, 'trackCode')
        teacher = list(teacherData.objects.filter(user_name=requestData['username']).values())
        recordTeacher = ''
        if len(teacher) > 0:
            recordTeacher = teacher[0]['teacher_name']
        studentPostTrack.objects.create(trackCode=index, studentCode=studentCode, studentName=studentName,
                                        studentSalary=studentSalary,
                                        recordTeacher=recordTeacher,
                                        enterpriseName=enterpriseName, postName=postName, postDuty=postDuty,
                                        remarks=remarks)
    updateTeacherName = teacherData.objects.filter(user_name=userName).values()[0]['teacher_name']
    if studentManage.objects \
            .filter(studentCode=studentCode) \
            .update(studentName=studentName, studentSex=studentSex, studentNativePlace=studentNativePlace,
                    professionCode=professionCode,
                    classesCode=classesCode, studentPhone=studentPhone, studentStatus=studentStatus,
                    teacherName=teacherName, teacherPhone=teacherPhone, employmentStatus=employmentStatus, updateTeacherName=updateTeacherName,
                    studentSalary=studentSalary, enterpriseCode=enterpriseCode, postCode=postCode,
                    postDuty=postDuty,
                    remarks=remarks):
        studentManage.objects.get(studentCode=studentCode).save()  # 更新修改时间
        return JsonResponse({'ret': 0, 'data': '修改基本信息成功!'})

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
    userList = []
    s_obj = studentManage.objects
    c_obj = classesManage.objects
    # 学生就业状态筛选
    if queryType == 'noSearch' and keyWord == '' and searchType in ['参军', '待安置', '已安置', '拟升学']:
        subData0 = list(s_obj.filter(employmentStatus=searchType, isDelete=False).values())
    else:
        subData0 = list(s_obj.filter(isDelete=False).values())

    # 学生属性筛选
    if queryType in ['studentCode', 'studentName', 'studentSex', 'studentNativePlace', 'employmentStatus'] and keyWord != '':
        search = {}
        key = queryType + '__icontains'
        search[key] = keyWord
        search['isDelete'] = False
        subData0 = list(s_obj.filter(**search).values())

    if queryType == 'classesName' and keyWord != '':
        # 1.查询此班级的编号,获取班级编号并set去重
        classesCodeList = set([i['classesCode'] for i in list(c_obj.filter(classesName__icontains=keyWord, isDelete=False).values())])
        # 2.利用此编号查询学生绑定班级专业表
        bindCode = []
        for i in classesCodeList:
            bindCode.extend(list(s_obj.filter(classesCode=i, isDelete=False).values()))
        # 3.存储有此班级编号的学号
        studentCodeList = [str(i['studentCode']) for i in bindCode]
        studentData = []
        for i in studentCodeList:
            studentData.extend(list(s_obj.filter(studentCode=i, isDelete=False).values()))
        subData0 = studentData
    # 自定义分页(提高系统运行速度)
    myData = listSplit(subData0, pageSize, pageNum)
    for i in myData['currentData']:
        # 获取所属专业,班级名称，班级届数并合并到学生信息列表中
        for ii in s_obj.filter(studentCode=i['studentCode'], isDelete=False).values():
            if ii['classesCode'] != '0':
                studentLevel = ''
                toClasses = ''
                toProfession = ''
                for iii in c_obj.filter(classesCode=ii['classesCode'], isDelete=False).values():
                    studentLevel = iii['classesLevel']
                    toClasses = iii['classesName']
                for iiii in professionManage.objects.filter(professionCode=ii['professionCode'], isDelete=False).values():
                    toProfession = iiii['professionName']
                i.update({'studentLevel': studentLevel, 'toProfession': toProfession, 'toClasses': toClasses})
            else:
                i.update({'studentLevel': '未绑定', 'toProfession': '未绑定', 'toClasses': '未绑定'})

        # 获取岗位信息和企业信息
        for studentBindData in list(s_obj.filter(studentCode=i['studentCode'], isDelete=False).values()):
            if studentBindData['postCode'] != '0':
                for postData in list(enterprisePost.objects.filter(postCode=studentBindData['postCode'], isDelete=False).values()):
                    i.update({'postName': postData['postName'], 'postAddress': postData['postAddress']})
            else:
                i.update({'postName': '未绑定', 'postAddress': '未绑定'})

            if studentBindData['enterpriseCode'] != '0':
                for enterpriseData in list(
                        enterpriseManage.objects.filter(enterpriseCode=studentBindData['enterpriseCode'], isDelete=False).values()):
                    i.update({'enterpriseName': enterpriseData['enterpriseName'],
                              'enterpriseAddress': enterpriseData['enterpriseAddress'],
                              'enterprisePhone': enterpriseData['enterprisePhone']})
            else:
                i.update({'enterpriseName': '未绑定', 'enterpriseAddress': '未绑定', 'enterprisePhone': '未绑定'})
        userList.append(i)

    return JsonResponse({
        'ret': 0,
        'data': userList,
        'pageNum': pageNum,
        'total': myData['dataSum'],
    })


def getProfessionAndClassesCascaderOptions(requestData):
    """
    获取专业数据及子菜单(班级)供学生页面联动菜单使用
    :param requestData:
    :return:
    """
    professionContainer = []
    for profession in professionManage.objects.filter(isDelete=False).values():
        kk = {'value': profession['professionCode'], 'label': profession['professionName'], 'disabled': True, 'children': []}
        classesList = []
        for classes in classesManage.objects.filter(professionCode=profession['professionCode'], isDelete=False).order_by('classesLevel').values():
            classesList.append({'value': classes['classesCode'], 'label': classes['classesName']})
        if len(classesList) > 0:
            kk.update({'disabled': False, 'children': classesList})
        else:
            kk.update({'disabled': True, 'children': []})
        professionContainer.append(kk)
    return JsonResponse({'ret': 0, 'data': professionContainer})


def getPostTrackData(requestData):
    """
    获取岗位追踪数据
    :param requestData:
    :return:
    """
    queryData = requestData['query']  # 查询的元数据
    keyWord = queryData['keyWord']  # 查询的关键词
    pageNum = queryData['pageNum']  # 当前页数
    pageSize = queryData['pageSize']  # 一页多少数据
    queryType = queryData['queryType']  # 搜索类型

    dataList = []
    obj = studentPostTrack.objects

    if queryType == 'noSearch':
        dataList = list(obj.filter(isDelete=False).values())

    if queryType == 'studentCode':
        dataList = list(obj.filter(studentCode__contains=keyWord, isDelete=False).values())

    if queryType == 'studentName':
        dataList = list(obj.filter(studentName__contains=keyWord, isDelete=False).values())

    if queryType == 'recordTeacher':
        dataList = list(obj.filter(recordTeacher__contains=keyWord, isDelete=False).values())

    paginator = Paginator(dataList, pageSize)  # 每页显示多少数据
    total = paginator.count  # 总数据量
    data = paginator.page(pageNum).object_list  # 某一页的数据

    return JsonResponse({
        'ret': 0,
        'data': data,
        'pageNum': pageNum,
        'total': total,
    })


def deletePostTrack(requestData):
    """
    删除岗位追踪数据
    :param requestData:
    :return:
    """
    trackCode = requestData['trackCode']
    if studentPostTrack.objects.filter(trackCode=trackCode).update(isDelete=True):
        return JsonResponse({'ret': 0, 'data': '删除学生岗位追踪信息成功!'})
    else:
        return JsonResponse({'ret': 1, 'data': '删除学生岗位追踪信息失败,请稍后重试!'})
