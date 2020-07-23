from django.db.models import Q
from django.http import JsonResponse

from utils.tools import listSplit
from .models import studentManage, professionManage, \
    classesManage, enterprisePost


def getWorkAreaData(requestData):
    """
    学生工作区域数据提取操作函数
    :param requestData:
    :return:
    """
    queryType = requestData['queryType']
    studentBaseData = []

    if queryType == 'getProfessionData':
        professionCode = requestData['queryInfo'][0]
        classesLevel = requestData['queryInfo'][1]
        # 提取此专业此届数有那些班级的班级编号
        classesData = []
        for i in list(classesManage.objects.filter(professionCode=professionCode, classesLevel=classesLevel,
                                                   isDelete=False).values()):
            classesData.append(str(i['classesCode']))
        studentBaseData = [i for i in
                           list(studentManage.objects.filter(professionCode=professionCode, isDelete=False).values()) if
                           i['classesCode'] in classesData]  # 获取学生基本数据并绑定专业及班级

    if queryType == 'getClassesData':
        professionCode = requestData['queryInfo'][0]
        classesLevel = requestData['queryInfo'][1]
        classesCode = requestData['queryInfo'][2]
        # 提取此专业此届数有那些班级的班级编号
        classesData = []
        for i in list(classesManage.objects.filter(classesCode=classesCode, classesLevel=classesLevel,
                                                   isDelete=False).values()):
            classesData.append(str(i['classesCode']))
        studentBaseData = [i for i in list(
            studentManage.objects.filter(professionCode=professionCode, classesCode=classesCode,
                                         isDelete=False).values()) if
                           i['classesCode'] in classesData]  # 获取学生基本数据并绑定专业及班级

    # 提取源数据
    qq = []
    for i in studentBaseData:
        for ii in enterprisePost.objects.filter(postCode=i['postCode'], isDelete=False).values():
            if ii['postAddress'].find('内蒙古自治区') != -1 or ii['postAddress'].find('黑龙江省', 0) != -1:
                qq.append({'name': ii['postAddress'][:3]})
                continue
            qq.append({'name': ii['postAddress'][:2]})
            continue

    # 过滤筛选数据去掉重复数据(用于统计) 或这个list(set(qq))
    kk = []
    for i in qq:
        if i not in kk:
            kk.append(i)

    # 次数统计
    data = []
    for i in kk:
        value = 0
        for ii in qq:
            if (ii['name'].find(i['name'])) != -1:
                value = value + 1
            i.update({'value': value})
        data.append(i)

    toolTipData = []
    for i in data:
        name = i['name']
        value = i['value']
        zz = {'name': name}
        for ii in data:
            if i['name'] == ii['name']:
                zz.update({'value': [{'name': '学生人数', 'value': value}]})
                continue
        toolTipData.append(zz)

    return JsonResponse({'ret': 0, 'data': data, 'toolTipData': toolTipData})


def getUnemployedRateData(requestData):
    """
    学生未就业数据获取函数
    :param requestData:
    :return:
    """
    queryType = requestData['queryType']

    studentList1 = []  # 组装包含绑定专业及班级的关系
    studentBaseData = []
    if queryType == 'getProfessionunemployedData':
        professionCode = requestData['queryInfo'][0]
        classesLevel = requestData['queryInfo'][1]
        # 提取此专业此届数有那些班级的班级编号
        classesData = []
        for i in list(classesManage.objects.filter(professionCode=professionCode, classesLevel=classesLevel,
                                                   isDelete=False).values()):
            classesData.append(str(i['classesCode']))
        studentBaseData = [i for i in
                           list(studentManage.objects.filter(professionCode=professionCode, isDelete=False).values()) if
                           i['classesCode'] in classesData]  # 获取学生基本数据并绑定专业及班级

    if queryType == 'getProfessioAndClassesnunemployedData':
        professionCode = requestData['queryInfo'][0]
        classesLevel = requestData['queryInfo'][1]
        classesCode = requestData['queryInfo'][2]
        # 提取此专业此届数有那些班级的班级编号
        classesData = []
        for i in list(classesManage.objects.filter(classesCode=classesCode, classesLevel=classesLevel,
                                                   isDelete=False).values()):
            classesData.append(str(i['classesCode']))
        studentBaseData = [i for i in list(
            studentManage.objects.filter(professionCode=professionCode, classesCode=classesCode,
                                         isDelete=False).values()) if
                           i['classesCode'] in classesData]  # 获取学生基本数据并绑定专业及班级

    for i in studentBaseData:
        if studentManage.objects.filter(studentCode=i['studentCode'], isDelete=False).count() > 0:
            for ii in studentManage.objects.filter(studentCode=i['studentCode'], isDelete=False).values():  # 获取到绑定关系
                i.update(ii)
                studentList1.append(i)
        else:
            i.update({'studentCode': i['studentCode'], 'professionCode': '-1', 'classesCode': '-1'})
            studentList1.append(i)

    # 替换专业代码为专业名称
    studentList2 = []
    for iii in studentList1:
        if str(iii['professionCode']) != '-1':
            for iiii in professionManage.objects.filter(professionCode=iii['professionCode'], isDelete=False).values():
                iii.update({'professionName': iiii['professionName']})
                studentList2.append(iii)
        else:
            iii.update({'professionName': '未绑定'})
            studentList2.append(iii)

    # 替换班级代码为班级名称
    studentList3 = []
    for student in studentList2:
        if str(student['classesCode']) != '-1':
            for classData in classesManage.objects.filter(classesCode=student['classesCode'], isDelete=False).values():
                student.update({'classesLevel': classData['classesLevel'], 'classesName': classData['classesName']})
                studentList3.append(student)
        else:
            student.update({'classesLevel': '未绑定', 'classesName': '未绑定'})
            studentList3.append(student)

    # 去掉无用字段组成最终数据
    studentList = []
    for studentData in studentList3:
        studentData.pop('classesCode')
        studentData.pop('professionCode')
        studentList.append(studentData)

    data = []  # 返回给客户端的数据
    peopleCount = len(studentList)  # 总人数
    for i in ['参军', '待安置', '已安置', '拟升学', '专升本']:
        value = 0  # 当前原因总共出现多少次
        for ii in studentList:
            if i == ii['employmentStatus']:
                value += 1

        classesInfo = []  # 保存班级最终的数据
        for className in classesManage.objects.filter(isDelete=False).values():
            classesContainer = {}  # 一个班级一个容器
            num = 0  # 当前班级当前原因有多少人
            for students in studentList:
                if students['employmentStatus'] == i and students['classesName'] == className['classesName']:
                    num += 1
                classesContainer.update({'classesName': className['classesName'], 'num': num})
            if num > 0:
                classesInfo.append(classesContainer)

        data.append({'name': i, 'value': value,
                     'classesData': classesInfo})

    return JsonResponse({'ret': 0, 'data': data, 'peopleCount': peopleCount})


def getSalaryData(requestData):
    """
    获取班级专业平均薪资数据
    :return:
    """
    type = requestData['queryType']

    if type == 'getProfessionSalaryData':
        professionCode = requestData['queryInfo'][0]
        classesLevel = requestData['queryInfo'][1]
        # 提取此专业此届数有那些班级的班级编号
        classesData = []
        for i in list(classesManage.objects.filter(professionCode=professionCode, classesLevel=classesLevel,
                                                   isDelete=False).values()):
            classesData.append(str(i['classesCode']))
        salaryList = [i['studentSalary'] for i in list(
            studentManage.objects.filter(professionCode=professionCode, employmentStatus='已安置',
                                         isDelete=False).values().order_by('studentSalary')) if
                      i['classesCode'] in classesData]  # 获取学生基本数据并绑定专业及班级

        # 专业平均工资
        salary = 0
        for i in salaryList:
            salary = salary + int(i)
        try:
            salary = salary / len(salaryList)
        except Exception:
            salary = 0.0

        # 专业最高工资
        try:
            maxSalary = int(salaryList[-1])
        except Exception:
            maxSalary = 0.0
        # 专业最低工资
        try:
            minSalary = int(salaryList[0])
        except Exception:
            minSalary = 0.0

        nameList = ['平均薪资', '最高薪资', '最低薪资']
        valueList = [format(salary, '.2f'), format(maxSalary, '.2f'), format(minSalary, '.2f')]

        return JsonResponse({'ret': 0, 'nameList': nameList, 'valueList': valueList})

    if type == 'getClassesSalaryData':
        professionCode = requestData['queryInfo'][0]
        classesLevel = requestData['queryInfo'][1]
        classesCode = requestData['queryInfo'][2]
        # 提取此专业此届数有那些班级的班级编号
        classesData = []
        for i in list(classesManage.objects.filter(classesCode=classesCode, classesLevel=classesLevel,
                                                   isDelete=False).values()):
            classesData.append(str(i['classesCode']))
        salaryList = [i['studentSalary'] for i in list(studentManage
                                                       .objects
                                                       .filter(professionCode=professionCode, classesCode=classesCode,
                                                               employmentStatus='已安置', isDelete=False)
                                                       .values().order_by('studentSalary')) if
                      i['classesCode'] in classesData]  # 获取学生基本数据并绑定专业及班级

        # 专业平均工资
        salary = 0
        for i in salaryList:
            salary = salary + int(i)

        try:
            salary = salary / len(salaryList)
        except Exception:
            salary = 0.0

        # 专业最高工资
        try:
            maxSalary = int(salaryList[-1])
        except Exception:
            maxSalary = 0.0
        # 专业最低工资
        try:
            minSalary = int(salaryList[0])
        except Exception:
            minSalary = 0.0

        nameList = ['平均薪资', '最高薪资', '最低薪资']
        valueList = [format(salary, '.2f'), format(maxSalary, '.2f'), format(minSalary, '.2f')]

        return JsonResponse({'ret': 0, 'nameList': nameList, 'valueList': valueList})


def getPeopleData(requestData):
    """
    获取男女人数
    :param requestData:
    :return:
    """
    # bodyMax:总人数 boyNum:男生人数 girlNum:女生人数
    # getClassesPeopleData      getProfessionPeopleData
    type = requestData['queryType']

    if type == 'getClassesPeopleData':
        professionCode = requestData['queryInfo'][0]
        classesLevel = requestData['queryInfo'][1]
        classesCode = requestData['queryInfo'][2]
        # 提取此专业此届数有那些班级的班级编号
        classesData = []
        for i in list(classesManage.objects.filter(classesCode=classesCode, classesLevel=classesLevel,
                                                   isDelete=False).values()):
            classesData.append(str(i['classesCode']))
        studentBaseData = [i for i in list(
            studentManage.objects.filter(professionCode=professionCode, classesCode=classesCode,
                                         isDelete=False).values()) if
                           i['classesCode'] in classesData]  # 获取学生基本数据并绑定专业及班级

        # 提取本班级有哪些学生
        boyNum = 0
        girlNum = 0
        for i in studentBaseData:
            for ii in studentManage.objects.filter(studentCode=i['studentCode'], studentSex='男生',
                                                   isDelete=False).values():
                boyNum = boyNum + 1
            for iii in studentManage.objects.filter(studentCode=i['studentCode'], studentSex='女生',
                                                    isDelete=False).values():
                girlNum = girlNum + 1
        bodyMax = boyNum + girlNum

        return JsonResponse({'ret': 0, 'bodyMax': bodyMax, 'boyNum': boyNum, 'girlNum': girlNum})

    if type == 'getProfessionPeopleData':
        professionCode = requestData['queryInfo'][0]
        classesLevel = requestData['queryInfo'][1]
        # 提取此专业此届数有那些班级的班级编号
        classesData = []
        for i in list(classesManage.objects.filter(professionCode=professionCode, isDelete=False).values()):
            for ii in list(
                    classesManage.objects.filter(classesCode=i['classesCode'], classesLevel=classesLevel,
                                                 isDelete=False).values()):
                if i['classesCode'] == ii['classesCode']:
                    classesData.append(str(i['classesCode']))
        studentBaseData = [i for i in
                           list(studentManage.objects.filter(professionCode=professionCode, isDelete=False).values()) if
                           i['classesCode'] in classesData]  # 获取学生基本数据并绑定专业及班级

        boyNum = 0
        girlNum = 0
        for i in studentBaseData:
            for ii in studentManage.objects.filter(studentCode=i['studentCode'], studentSex='男生',
                                                   isDelete=False).values():
                boyNum = boyNum + 1
            for iii in studentManage.objects.filter(studentCode=i['studentCode'], studentSex='女生',
                                                    isDelete=False).values():
                girlNum = girlNum + 1
        bodyMax = boyNum + girlNum
        return JsonResponse({'ret': 0, 'bodyMax': bodyMax, 'boyNum': boyNum, 'girlNum': girlNum})


def getIndexData(requestData):
    """
    获取首页数据
    :param requestData:
    :return:
    """
    postCount = enterprisePost.objects.filter(isDelete=False).values().count()
    unemployedCount = studentManage.objects.filter(
        Q(employmentStatus='参军') | Q(employmentStatus='拟升学') | Q(employmentStatus='待安置'),
        isDelete=False).values().count()
    employmentCount = studentManage.objects.filter(employmentStatus='已安置', isDelete=False).values().count()
    studentSumCount = studentManage.objects.filter(isDelete=False).values().count()
    professionSumCount = professionManage.objects.filter(isDelete=False).values().count()
    classesSumCount = classesManage.objects.filter(isDelete=False).values().count()
    boySumCount = studentManage.objects.filter(studentSex='男生', isDelete=False).values().count()
    girlSumCount = studentManage.objects.filter(studentSex='女生', isDelete=False).values().count()

    return JsonResponse(
        {'ret': 0, 'postCount': postCount, 'unemployedCount': unemployedCount,
         'employmentCount': employmentCount,
         'studentSumCount': studentSumCount, 'professionSumCount': professionSumCount,
         'classesSumCount': classesSumCount,
         'boySumCount': boySumCount, 'girlSumCount': girlSumCount})


def getWorkDirection(requestData):
    """
    工作方向男女占比
    :param requestData:
    :return:
    """
    query = requestData['query']
    pageNum = query['pageNum']  # 当前页数
    pageSize = query['pageSize']  # 一页多少数据

    studentList1 = []  # 组装包含绑定专业及班级的关系
    studentBaseData = studentManage.objects.filter(employmentStatus='已安置', isDelete=False).values()  # 获取学生基本数据并绑定专业及班级
    for i in studentBaseData:
        for ii in studentManage.objects.filter(studentCode=i['studentCode'], isDelete=False).values():  # 获取到绑定关系
            i.update(ii)
            studentList1.append(i)

    # 替换专业代码为专业名称
    studentList2 = []
    for iii in studentList1:
        for iiii in professionManage.objects.filter(professionCode=iii['professionCode'], isDelete=False).values():
            iii.update({'professionName': iiii['professionName']})
            studentList2.append(iii)

    # 替换班级代码为班级名称
    studentList3 = []
    for student in studentList2:
        for classData in classesManage.objects.filter(classesCode=student['classesCode'], isDelete=False).values():
            student.update({'classesLevel': classData['classesLevel'], 'classesName': classData['classesName']})
            studentList3.append(student)

    # 去掉无用字段组成最终数据
    studentList = []
    for studentData in studentList3:
        studentData.pop('classesCode')
        studentData.pop('professionCode')
        for i in enterprisePost.objects.filter(postCode=studentData['postCode'], isDelete=False).values():
            if str(studentData['postCode']) == str(i['postCode']):
                studentData.update(i)
        studentList.append(studentData)

    # 保存年份
    yearData = []
    yearData1 = []
    for year in studentList:
        if year['classesLevel'] not in yearData1:
            yearData1.append(year['classesLevel'])
    yearData1.sort(key=None, reverse=False)  # 年份排序(从小到大)

    # 只统计最近5年的
    if len(yearData1) > 5:
        yearData = yearData1[-5:]
    else:
        yearData = yearData1

    # 统计学生的岗位
    studentPost = []
    for post in studentList:
        if post['employmentStatus'] == '已安置':
            if post['postName'] not in studentPost:
                studentPost.append(post['postName'])

    postBoyCountAndClassesLevel = {}  # 男生最终数据
    for classesLevel in yearData:  # 统计这一年的这些工作男孩有多少
        postStudentCountBoyData = []
        for postCount in studentPost:  # 统计该岗位男生人数
            postStudentCount = 0
            for student in studentList:
                if postCount == student['postName'] and student['employmentStatus'] == '已安置' and \
                        student['studentSex'] == '男生' and classesLevel == student['classesLevel']:
                    postStudentCount = postStudentCount + 1
            postStudentCountBoyData.append(postStudentCount)
        postBoyCountAndClassesLevel.update({classesLevel: listSplit(postStudentCountBoyData, pageSize, pageNum)['currentData']})

    postGirlCountAndClassesLevel = {}  # 女生最终数据
    for classesLevel1 in yearData:  # 统计这一年的这些工作女孩有多少
        postStudentCountGirlData = []
        for postCount1 in studentPost:  # 统计该岗位女生人数
            postStudentCount1 = 0
            for student1 in studentList:
                if postCount1 == student1['postName'] and student1['employmentStatus'] == '已安置' and student1[
                    'studentSex'] == '女生' and classesLevel1 == student1['classesLevel']:
                    postStudentCount1 = postStudentCount1 + 1
            postStudentCountGirlData.append(postStudentCount1)
        postGirlCountAndClassesLevel.update({classesLevel1: listSplit(postStudentCountGirlData, pageSize, pageNum)['currentData']})

    # 对数据数量进行分页，优化前端数据显示效果
    studentPost = listSplit(studentPost, pageSize, pageNum)

    return JsonResponse({'ret': 0, 'pagination': {'total': studentPost['dataSum'], 'pageSum': studentPost['pageSum']},
                         'yearData': yearData, 'studentPost': studentPost['currentData'],
                         'postBoyCountAndClassesLevel': postBoyCountAndClassesLevel,
                         'postGirlCountAndClassesLevel': postGirlCountAndClassesLevel})
