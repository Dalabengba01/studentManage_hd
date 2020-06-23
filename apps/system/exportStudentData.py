import os

from django.http import StreamingHttpResponse, JsonResponse
from xlwt import *

from .models import studentManage, professionManage, classesManage, enterprisePost, enterpriseManage


def getexportStudentData(request):
    """
    导出学生数据为Excel表格(学生数据=基本数据+已就业数据|未就业数据),新增sheet包含专业，班级 ，企业，岗位详细信息
    :param request: 包含用户请求的参数
    :return: 返回文件流对象
    """
    searchType = request['getDataType']

    # 创建新的列表供后续功能操作
    subData0 = []

    obj = studentManage.objects

    if searchType in ['全部', '参军', '待安置', '已安置', '拟升学']:

        if searchType == '全部':
            subData0 = list(obj.filter(isDelete=False).values())

        if searchType == '参军':
            subData0 = list(obj.filter(isDelete=False, employmentStatus='参军').values())

        if searchType == '待安置':
            subData0 = list(obj.filter(isDelete=False, employmentStatus='待安置').values())

        if searchType == '已安置':
            subData0 = list(obj.filter(isDelete=False, employmentStatus='已安置').values())

        if searchType == '拟升学':
            subData0 = list(obj.filter(isDelete=False, employmentStatus='拟升学').values())

    userList = []
    for i in subData0:
        # 获取所属专业,班级名称，班级届数并合并到学生信息列表中
        for ii in obj.filter(isDelete=False, studentCode=i['studentCode']).values():
            if ii['classesCode'] != '0':
                studentLevel = ''
                toClasses = ''
                toProfession = ''
                for iii in classesManage.objects.filter(isDelete=False, classesCode=ii['classesCode']).values():
                    studentLevel = iii['classesLevel']
                    toClasses = iii['classesName']
                for iiii in professionManage.objects.filter(isDelete=False,
                                                            professionCode=ii['professionCode']).values():
                    toProfession = iiii['professionName']
                i.update({'studentLevel': studentLevel, 'toProfession': toProfession, 'toClasses': toClasses})
            else:
                i.update({'studentLevel': '未绑定', 'toProfession': '未绑定', 'toClasses': '未绑定'})

        # 获取岗位信息和企业信息
        for studentBindData in list(obj.filter(isDelete=False, studentCode=i['studentCode']).values()):
            if studentBindData['postCode'] != '0':
                for postData in list(
                        enterprisePost.objects.filter(isDelete=False, postCode=studentBindData['postCode']).values()):
                    i.update({'postDuty': postData['postDuty'], 'postName': postData['postName'], 'postAddress': postData['postAddress']})
            else:
                i.update({'postDuty': '未绑定', 'postName': '未绑定', 'postAddress': '未绑定'})

            if studentBindData['enterpriseCode'] != '0':
                for enterpriseData in list(
                        enterpriseManage.objects.filter(isDelete=False,
                                                        enterpriseCode=studentBindData['enterpriseCode']).values()):
                    i.update({'enterpriseName': enterpriseData['enterpriseName'],
                              'enterpriseAddress': enterpriseData['enterpriseAddress'],
                              'enterprisePhone': enterpriseData['enterprisePhone']})
            else:
                i.update({'enterpriseName': '未绑定', 'enterpriseAddress': '未绑定', 'enterprisePhone': '未绑定'})
        userList.append(i)

    excelData = []
    excelTitle = ''
    if searchType == '全部':
        excelData = userList
        excelTitle = '中兴创新学院学生就业管理系统(学生全部数据)'

    if searchType == '参军':
        excelData = [i for i in userList if i['employmentStatus'] == '参军']
        excelTitle = '中兴创新学院学生就业管理系统(参军学生数据)'

    if searchType == '待安置':
        excelData = [i for i in userList if i['employmentStatus'] == '待安置']
        excelTitle = '中兴创新学院学生就业管理系统(待安置学生数据)'

    if searchType == '已安置':
        excelData = [i for i in userList if i['employmentStatus'] == '已安置']
        excelTitle = '中兴创新学院学生就业管理系统(已安置学生数据)'

    if searchType == '拟升学':
        excelData = [i for i in userList if i['employmentStatus'] == '拟升学']
        excelTitle = '中兴创新学院学生就业管理系统(拟升学学生数据)'

    if len(excelData) > 0:
        # 创建工作薄
        ws = Workbook(encoding='utf-8')
        student = ws.add_sheet(u"学生数据")
        # 设置列宽
        colWidth = [256 * 10, 256 * 25, 256 * 20, 256 * 10, 256 * 15, 256 * 30, 256 * 20, 256 * 25, 256 * 25, 256 * 20,
                    256 * 30, 256 * 30, 256 * 20, 256 * 20, 256 * 25, 256 * 30, 256 * 20, 256 * 20, 256 * 20, 256 * 20,
                    256 * 15,
                    256 * 30,
                    256 * 30]
        colNum = 0
        for i in colWidth:
            student.col(colNum).width = i
            colNum = colNum + 1
        # 设置行高
        student.row(0).set_style(easyxf('font:height 720'))

        # 设置单元格样式(对其方式)内容样式
        style = XFStyle()  # 创建一个样式对象，初始化样式
        al = Alignment()  # 创建对其方式对象
        al.horz = 0x02  # 设置水平居中
        al.vert = 0x01  # 设置垂直居中
        style.alignment = al

        myStyle = XFStyle()
        al1 = Alignment()
        al1.horz = 0x02  # 设置水平居中
        al1.vert = 0x01  # 设置垂直居中
        myStyle.alignment = al1
        pattern = Pattern()
        pattern.pattern = Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = Style.colour_map['blue_gray']  # 设置单元格背景色
        myStyle.pattern = pattern

        # 标题样式
        style1 = XFStyle()
        font = Font()  # 创建字体样式对象
        font.height = 20 * 20  # 字体大小，11为字号，20为衡量单位
        font.bold = True  # 字体加粗
        style1.font = font
        al = Alignment()  # 创建对其方式对象
        al.horz = 0x02  # 设置水平居中
        al.vert = 0x01  # 设置垂直居中
        style1.alignment = al

        # 设置表头
        tableHeader = ['序号', '学生学号', '学生姓名', '学生性别', '学生届数', '所属专业', '所属班级', '学生籍贯', '学生电话', '就业状态', '企业名称', '企业地址',
                       '企业联系方式', '岗位名称', '工作地址', '岗位职责', '最新薪资', '直属主管', '主管电话', '更新教师', '学生状态', '备注', '修改时间']
        col = 0
        for i in tableHeader:
            student.write(1, col, i, style)
            col = col + 1

        # 写入数据(第一行是标题，第二行表头，第三行开始写数据)
        excel_row = 2

        student.write_merge(0, 0, 0, 12, excelTitle, style1)
        index = 0
        for obj in excelData:
            index = index + 1
            studentCode = obj['studentCode']
            studentName = obj['studentName']
            studentSex = obj['studentSex']
            studentLevel = obj['studentLevel']
            toProfession = obj['toProfession']
            toClasses = obj['toClasses']
            studentNativePlace = obj['studentNativePlace']
            studentPhone = obj['studentPhone']
            employmentStatus = obj['employmentStatus']
            enterpriseName = obj['enterpriseName']
            enterpriseAddress = obj['enterpriseAddress']
            enterprisePhone = obj['enterprisePhone']
            postName = obj['postName']
            postAddress = obj['postAddress']
            postDuty = obj['postDuty']
            studentSalary = obj['studentSalary']
            teacherName = obj['teacherName']
            teacherPhone = obj['teacherPhone']
            updateTeacherName = obj['updateTeacherName']
            studentStatus = obj['studentStatus']
            remarks = obj['remarks']
            addTime = obj['addTime'].strftime("%Y-%m-%d %H:%M:%S")[:19]

            student.write(excel_row, 0, index, style)
            student.write(excel_row, 1, studentCode, style)
            student.write(excel_row, 2, studentName, style)
            student.write(excel_row, 3, studentSex, style)
            student.write(excel_row, 4, studentLevel, style)
            student.write(excel_row, 5, toProfession, style)
            student.write(excel_row, 6, toClasses, style)
            student.write(excel_row, 7, studentNativePlace, style)
            student.write(excel_row, 8, studentPhone, style)
            student.write(excel_row, 9, employmentStatus, style)
            student.write(excel_row, 10, enterpriseName, style)
            student.write(excel_row, 11, enterpriseAddress, style)
            student.write(excel_row, 12, enterprisePhone, style)
            student.write(excel_row, 13, postName, style)
            student.write(excel_row, 14, postAddress, style)
            student.write(excel_row, 15, postDuty, style)
            student.write(excel_row, 16, studentSalary, style)
            student.write(excel_row, 17, teacherName, style)
            student.write(excel_row, 18, teacherPhone, style)
            student.write(excel_row, 19, updateTeacherName, style)
            student.write(excel_row, 20, studentStatus, style)
            student.write(excel_row, 21, remarks, style)
            student.write(excel_row, 22, addTime, style)
            excel_row += 1

        ####################### 专业班级数据 #######################
        # 合成专业班级数据
        professionData = []
        for profession in list(professionManage.objects.filter(isDelete=False).values()):
            for classes in classesManage.objects.filter(professionCode=profession['professionCode'],
                                                        isDelete=False).values():
                professionData.append(
                    {'professionCode': profession['professionCode'], 'professionName': profession['professionName'],
                     'classesLevel': classes['classesLevel'], 'classesCode': classes['classesCode'],
                     'classesName': classes['classesName']})

        profession = ws.add_sheet(u"专业班级数据")
        # 设置列宽
        colWidth = [256 * 10, 256 * 25, 256 * 15, 256 * 20]
        colNum = 0
        for i in colWidth:
            profession.col(colNum).width = i
            colNum = colNum + 1
        # 设置行高
        profession.row(0).set_style(easyxf('font:height 720'))
        # 设置表头
        tableHeader = ['序号', '专业名称', '班级届数', '班级名称']
        col = 0
        for i in tableHeader:
            profession.write(1, col, i, style)
            col = col + 1

        # 写入数据(第一行是标题，第二行表头，第三行开始写数据)
        excel_row = 2

        profession.write_merge(0, 0, 0, 12, '中兴创新学院学生就业管理系统(专业班级数据)', style1)
        index = 0
        for obj in professionData:
            index = index + 1
            professionName = obj['professionName']
            classesLevel = obj['classesLevel']
            classesName = obj['classesName']

            profession.write(excel_row, 0, index, style)
            profession.write(excel_row, 1, professionName, style)
            profession.write(excel_row, 2, classesLevel, style)
            profession.write(excel_row, 3, classesName, style)
            excel_row += 1

        ####################### 企业岗位数据 #######################
        enterpriseData = []
        for enterprise in list(enterpriseManage.objects.filter(isDelete=False).values()):
            for post in list(enterprisePost.objects.filter(enterpriseCode=enterprise['enterpriseCode'],
                                                           isDelete=False).values()):
                enterpriseData.append(
                    {'enterpriseName': enterprise['enterpriseName'], 'enterpriseScale': enterprise['enterpriseScale'],
                     'goodGrade': enterprise['goodGrade'], 'enterpriseContacts': enterprise['enterpriseContacts'],
                     'enterprisePhone': enterprise['enterprisePhone'],
                     'enterpriseAddress': enterprise['enterpriseAddress'], 'remarks': enterprise['remarks'],
                     'skyEyeScore': enterprise['skyEyeScore'],
                     'postName': post['postName'],
                     'postAddress': post['postAddress'], 'salaryTreatment': post['salaryTreatment'],
                     'recruitCount': post['recruitCount']})

        enterprise = ws.add_sheet(u"企业岗位数据")
        # 设置列宽
        colWidth = [256 * 10, 256 * 30, 256 * 10, 256 * 10, 256 * 15, 256 * 30, 256 * 30, 256 * 20, 256 * 10, 256 * 10,
                    256 * 30, 256 * 30]
        colNum = 0
        for i in colWidth:
            enterprise.col(colNum).width = i
            colNum = colNum + 1
        # 设置行高
        enterprise.row(0).set_style(easyxf('font:height 720'))
        # 设置表头
        tableHeader = ['序号', '企业名称', '企业规模', '优质等级', '联系人姓名', '联系方式', '企业地址', '备注', '天眼查分数', '岗位名称', '工作地点', '工资待遇',
                       '招聘人数']
        col = 0
        for i in tableHeader:
            enterprise.write(1, col, i, style)
            col = col + 1

        # 写入数据(第一行是标题，第二行表头，第三行开始写数据)
        excel_row = 2

        enterprise.write_merge(0, 0, 0, 12, '中兴创新学院学生就业管理系统(企业岗位数据)', style1)
        index = 0
        for obj in enterpriseData:
            index = index + 1
            enterpriseName = obj['enterpriseName']
            enterpriseScale = obj['enterpriseScale']
            goodGrade = obj['goodGrade']
            enterpriseContacts = obj['enterpriseContacts']
            enterprisePhone = obj['enterprisePhone']
            enterpriseAddress = obj['enterpriseAddress']
            remarks = obj['remarks']
            skyEyeScore = obj['skyEyeScore']
            postName = obj['postName']
            postAddress = obj['postAddress']
            salaryTreatment = obj['salaryTreatment']
            recruitCount = obj['recruitCount']

            enterprise.write(excel_row, 0, index, style)
            enterprise.write(excel_row, 1, enterpriseName, style)
            enterprise.write(excel_row, 2, enterpriseScale, style)
            enterprise.write(excel_row, 3, goodGrade, style)
            enterprise.write(excel_row, 4, enterpriseContacts, style)
            enterprise.write(excel_row, 5, enterprisePhone, style)
            enterprise.write(excel_row, 6, enterpriseAddress, style)
            enterprise.write(excel_row, 7, remarks, style)
            enterprise.write(excel_row, 8, skyEyeScore, style)
            enterprise.write(excel_row, 9, postName, style)
            enterprise.write(excel_row, 10, postAddress, style)
            enterprise.write(excel_row, 11, salaryTreatment, style)
            enterprise.write(excel_row, 12, recruitCount, style)
            excel_row += 1

        # 检测文件是够存在
        # 方框中代码是保存本地文件使用，如不需要请删除该代码
        ###########################
        fileName = 'studentData.xls'
        currPath = os.path.abspath('.')
        savePath = currPath + '/static/' + fileName
        exist_file = os.path.exists(savePath)
        if exist_file:
            os.remove(savePath)
        ws.save(savePath)

        ############################
        # 显示在弹出对话框中的默认的下载文件名
        the_file_name = fileName

        def file_iterator(file_name, chunk_size=512):
            with open(file_name, 'rb') as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        # 获取当前路径
        cur_path = os.path.abspath('.')
        # 设置生成文件所在路径
        download_url = cur_path + '/static/'

        response = StreamingHttpResponse(file_iterator(download_url + fileName))
        response['Content-Type'] = 'application/vnd.ms-excel'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
        return response
    else:
        return JsonResponse({'ret': 1, 'data': '此类型数据为空，不提供下载！'})
