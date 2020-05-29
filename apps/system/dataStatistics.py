from django.http import JsonResponse

from .models import studentManage, professionManage, \
    classesManage, enterprisePost


def getWorkAreaData(requestData):
    """
    学生工作区域数据提取操作函数
    :param requestData:
    :return:
    """
    # 提取源数据
    qq = []
    studentList = [i for i in studentManage.objects.filter(employmentStatus='已安置').values()]
    for i in studentList:
        for ii in enterprisePost.objects.filter(postCode=i['postCode']).values():
            if ii['postAddress'].find('内蒙古自治区') != -1 or ii['postAddress'].find('黑龙江省', 0) != -1:
                qq.append({'name': ii['postAddress'][:3]})
                continue
            qq.append({'name': ii['postAddress'][:2]})
            continue

    # 过滤筛选数据去掉重复数据 或这个list(set(qq))
    kk = []
    for i in qq:
        if i not in kk:
            kk.append(i)

    # 次数统计
    data = []
    for i in kk:
        value = 0
        for ii in enterprisePost.objects.values():
            if (ii['postAddress'].find(i['name'])) != -1:
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
    studentList1 = []  # 组装包含绑定专业及班级的关系
    studentBaseData = studentManage.objects.filter().values()  # 获取学生基本数据并绑定专业及班级
    for i in studentBaseData:
        if studentManage.objects.filter(studentCode=i['studentCode']).count() > 0:
            for ii in studentManage.objects.filter(studentCode=i['studentCode']).values():  # 获取到绑定关系
                i.update(ii)
                studentList1.append(i)
        else:
            i.update({'studentCode': i['studentCode'], 'professionCode': '-1', 'classesCode': '-1'})
            studentList1.append(i)

    # 替换专业代码为专业名称
    studentList2 = []
    for iii in studentList1:
        if str(iii['professionCode']) != '-1':
            for iiii in professionManage.objects.filter(professionCode=iii['professionCode']).values():
                iii.update({'professionName': iiii['professionName']})
                studentList2.append(iii)
        else:
            iii.update({'professionName': '未绑定'})
            studentList2.append(iii)

    # 替换班级代码为班级名称
    studentList3 = []
    for student in studentList2:
        if str(student['classesCode']) != '-1':
            for classData in classesManage.objects.filter(classesCode=student['classesCode']).values():
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
    for i in ['参军', '待安置', '已安置', '拟升学']:
        value = 0  # 当前原因总共出现多少次
        for ii in studentList:
            if i == ii['employmentStatus']:
                value += 1

        classesInfo = []  # 保存班级最终的数据
        for className in classesManage.objects.filter().values():
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
    获取班级专业平均工资数据
    :return:
    """
    type = requestData['type']

    if type == 'getClassesSalaryData':
        classesCode = requestData['classesCode']
        studentCodeArray = []
        # 提取该班级的学生学号
        for i in studentManage.objects.filter(classesCode=classesCode).values():
            studentCodeArray.append(int(i['studentCode']))
        salary = 0
        employmentCount = 0
        for i in studentCodeArray:
            for ii in studentManage.objects.filter(studentCode=i, employmentStatus='已安置').values():
                employmentCount = employmentCount + 1
                # 解决信息首次录入为已就业状态信息未补全导致的BUG
                # if ii['studentSalary'] == '':
                #     continue
                salary = salary + int(ii['studentSalary'])
        # 计算该班级平均工资
        if len(studentCodeArray) <= 0:
            salary = 0
        elif employmentCount == 0:
            employmentCount = 1
        try:
            salary = salary / employmentCount
        except ZeroDivisionError:
            salary = 0.0
        data = []
        data.append(format(salary, '.2f'))
        return JsonResponse({'ret': 0, 'data': data})

    if type == 'getProfessionSalaryData':
        # 统计有哪些专业
        professionCodeArray = []
        for i in professionManage.objects.values():
            if i['professionCode'] not in professionCodeArray:
                professionCodeArray.append(
                    {'professionCode': i['professionCode'], 'professionName': i['professionName']})

        # 提取专业学生
        professionContainer = []
        for i in professionCodeArray:
            studentContainer = []
            for ii in studentManage.objects.filter(professionCode=i['professionCode']).values():
                studentContainer.append(ii['studentCode'])
            professionContainer.append({'professionCode': i['professionCode'], 'professionName': i['professionName'],
                                        'students': studentContainer})

        # 提取学生工资
        nameList = []
        valueList = []
        for i in professionContainer:
            salary = 0
            employmentCount = 0
            for ii in i['students']:
                for iii in studentManage.objects.filter(studentCode=ii, employmentStatus='已安置').values():
                    employmentCount = employmentCount + 1
                    salary = salary + int(iii['studentSalary'])
            if len(i['students']) <= 0:
                continue
            nameList.append(i['professionName'])
            if employmentCount == 0:
                employmentCount = 1
            salary = format(salary / employmentCount, '.2f')
            valueList.append(salary)
        return JsonResponse({'ret': 0, 'nameList': nameList, 'valueList': valueList})


def getPeopleData(requestData):
    """
    获取男女人数
    :param requestData:
    :return:
    """
    # bodyMax:总人数 boyNum:男生人数 girlNum:女生人数
    # getClassesPeopleData      getProfessionPeopleData
    type = requestData['type']

    if type == 'getClassesPeopleData':
        classesCode = requestData['classesCode']
        # 提取本班级有哪些学生
        boyNum = 0
        girlNum = 0
        for i in studentManage.objects.filter(classesCode=classesCode).values():
            for ii in studentManage.objects.filter(studentCode=i['studentCode'], studentSex='男生').values():
                boyNum = boyNum + 1
            for iii in studentManage.objects.filter(studentCode=i['studentCode'], studentSex='女生').values():
                girlNum = girlNum + 1
        bodyMax = boyNum + girlNum

        return JsonResponse({'ret': 0, 'bodyMax': bodyMax, 'boyNum': boyNum, 'girlNum': girlNum})

    if type == 'getProfessionPeopleData':
        professionCode = requestData['professionCode']
        boyNum = 0
        girlNum = 0
        for i in studentManage.objects.filter(professionCode=professionCode).values():
            for ii in studentManage.objects.filter(studentCode=i['studentCode'], studentSex='男生').values():
                boyNum = boyNum + 1
            for iii in studentManage.objects.filter(studentCode=i['studentCode'], studentSex='女生').values():
                girlNum = girlNum + 1
        bodyMax = boyNum + girlNum
        return JsonResponse({'ret': 0, 'bodyMax': bodyMax, 'boyNum': boyNum, 'girlNum': girlNum})


def getIndexData(requestData):
    """
    获取首页数据
    :param requestData:
    :return:
    """
    employmentStatusCount = 0
    unemployedCount = studentManage.objects.exclude(employmentStatus='已安置').values().count()
    employmentCount = studentManage.objects.filter(employmentStatus='已安置').values().count()
    studentSumCount = studentManage.objects.filter().values().count()
    professionSumCount = professionManage.objects.filter().values().count()
    classesSumCount = classesManage.objects.filter().values().count()
    boySumCount = studentManage.objects.filter(studentSex='男生').values().count()
    girlSumCount = studentManage.objects.filter(studentSex='女生').values().count()

    return JsonResponse(
        {'ret': 0, 'employmentStatusCount': employmentStatusCount, 'unemployedCount': unemployedCount,
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
    studentList1 = []  # 组装包含绑定专业及班级的关系
    studentBaseData = studentManage.objects.filter(employmentStatus='已安置').values()  # 获取学生基本数据并绑定专业及班级
    for i in studentBaseData:
        for ii in studentManage.objects.filter(studentCode=i['studentCode']).values():  # 获取到绑定关系
            i.update(ii)
            studentList1.append(i)

    # 替换专业代码为专业名称
    studentList2 = []
    for iii in studentList1:
        for iiii in professionManage.objects.filter(professionCode=iii['professionCode']).values():
            iii.update({'professionName': iiii['professionName']})
            studentList2.append(iii)

    # 替换班级代码为班级名称
    studentList3 = []
    for student in studentList2:
        for classData in classesManage.objects.filter(classesCode=student['classesCode']).values():
            student.update({'classesLevel': classData['classesLevel'], 'classesName': classData['classesName']})
            studentList3.append(student)

    # 去掉无用字段组成最终数据
    studentList = []
    for studentData in studentList3:
        studentData.pop('classesCode')
        studentData.pop('professionCode')
        for i in enterprisePost.objects.filter(postCode=studentData['postCode']).values():
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
                if postCount == student['postName'] and student['employmentStatus'] == '已安置' and student[
                    'studentSex'] == '男生' and classesLevel == student['classesLevel']:
                    postStudentCount = postStudentCount + 1
            postStudentCountBoyData.append(postStudentCount)
        postBoyCountAndClassesLevel.update({classesLevel: postStudentCountBoyData})

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
        postGirlCountAndClassesLevel.update({classesLevel1: postStudentCountGirlData})

    return JsonResponse({'ret': 0, 'yearData': yearData, 'studentPost': studentPost,
                         'postBoyCountAndClassesLevel': postBoyCountAndClassesLevel,
                         'postGirlCountAndClassesLevel': postGirlCountAndClassesLevel})
