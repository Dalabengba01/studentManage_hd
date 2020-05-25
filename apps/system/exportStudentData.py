import os

from django.http import StreamingHttpResponse, JsonResponse
from xlwt import *

from .models import studentManage, studentBindClassesAndProfession, professionManage, classesManage, \
    employmentReturnVisit


def getexportStudentData(request):
    """
    导出学生数据为Excel表格(学生数据=基本数据+已就业数据|未就业数据)
    :param request: 包含用户请求的参数
    :return: 返回文件流对象
    """
    searchType = request['getDataType']
    studentList1 = []  # 组装包含绑定专业及班级的关系
    studentBaseData = studentManage.objects.filter().values()  # 获取学生基本数据
    for i in studentBaseData:
        if studentBindClassesAndProfession.objects.filter(studentCode=i['studentCode']).count() > 0:
            for ii in studentBindClassesAndProfession.objects.filter(studentCode=i['studentCode']).values():  # 获取到绑定关系
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

    # 添加回访信息数据
    returnVisit = []
    for visit in employmentReturnVisit.objects.values():
        data = {}
        for student in studentList:
            if str(visit['studentCode']) == str(student['studentCode']):
                data.update(visit)
                data.update(student)
        returnVisit.append(data)

    excelData = []
    excelTitle = ''
    if searchType == '全部':
        excelData = returnVisit
        excelTitle = '中兴创新学院学生就业管理系统(学生全部数据)'

    if searchType == '参军':
        excelData = [i for i in returnVisit if i['employmentStatus'] == '参军']
        excelTitle = '中兴创新学院学生就业管理系统(参军学生数据)'

    if searchType == '待安置':
        excelData = [i for i in returnVisit if i['employmentStatus'] == '待安置']
        excelTitle = '中兴创新学院学生就业管理系统(待安置学生数据)'

    if searchType == '已安置':
        excelData = [i for i in returnVisit if i['employmentStatus'] == '已安置']
        excelTitle = '中兴创新学院学生就业管理系统(已安置学生数据)'

    if searchType == '拟升学':
        excelData = [i for i in returnVisit if i['employmentStatus'] == '拟升学']
        excelTitle = '中兴创新学院学生就业管理系统(拟升学学生数据)'

    if len(excelData) > 0:
        # 创建工作薄
        ws = Workbook(encoding='utf-8')
        w = ws.add_sheet(u"学生数据")
        # 设置列宽
        colWidth = [256 * 10, 256 * 10, 256 * 20, 256 * 15, 256 * 10, 256 * 10, 256 * 10, 256 * 25, 256 * 20, 256 * 20,
                    256 * 25, 256 * 22]
        colNum = 0
        for i in colWidth:
            w.col(colNum).width = i
            colNum = colNum + 1
        # 设置行高
        w.row(0).set_style(easyxf('font:height 720'))

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
        w.write(1, 0, "序号", style)
        w.write(1, 1, "学生届数", style)
        w.write(1, 2, "所属专业", style)
        w.write(1, 3, "所属班级", style)
        w.write(1, 4, "学生学号", style)
        w.write(1, 5, "学生姓名", style)
        w.write(1, 6, "学生性别", style)
        w.write(1, 7, "学生电话", style)
        w.write(1, 8, "就业状态", style)
        w.write(1, 9, "实习单位名称", style)
        w.write(1, 10, "实习单位地址", style)
        w.write(1, 11, "岗位名称", style)
        w.write(1, 12, "实习薪资", style)
        w.write(1, 13, "实习单位电话", style)
        w.write(1, 14, "指导老师姓名", style)
        w.write(1, 15, "指导老师电话", style)
        w.write(1, 16, "学生状态", style)
        w.write(1, 17, "创建时间", style)
        w.write(1, 18, "1月回访情况", style)
        w.write(1, 19, "2月回访情况", style)
        w.write(1, 20, "3月回访情况", style)
        w.write(1, 21, "4月回访情况", style)
        w.write(1, 22, "5月回访情况", style)
        w.write(1, 23, "6月回访情况", style)
        w.write(1, 24, "7月回访情况", style)
        w.write(1, 25, "8月回访情况", style)
        w.write(1, 26, "9月回访情况", style)
        w.write(1, 27, "10月回访情况", style)
        w.write(1, 28, "11月回访情况", style)
        w.write(1, 29, "12月回访情况", style)

        # 写入数据(第一行是标题，第二行表头，第三行开始写数据)
        excel_row = 2

        w.write_merge(0, 0, 0, 12, excelTitle, style1)
        index = 0
        for obj in excelData:
            index = index + 1
            classesLevel = obj['classesLevel']
            professionName = obj['professionName']
            classesName = obj['classesName']
            studentCode = str(obj['studentCode'])
            studentName = obj['studentName']
            studentSex = obj['studentSex']
            studentPhone = obj['studentPhone']
            employmentStatus = obj['employmentStatus']
            companyName = obj['companyName']
            companyAddress = obj['companyAddress']
            postName = obj['postName']
            studentSalary = obj['studentSalary']
            companyPhone = obj['companyPhone']
            teacherName = obj['teacherName']
            teacherPhone = obj['teacherPhone']
            studentStatus = obj['studentStatus']
            addTime = obj['addTime'].strftime("%Y-%m-%d")[:10]
            data1 = obj['data1']
            data2 = obj['data2']
            data3 = obj['data3']
            data4 = obj['data4']
            data5 = obj['data5']
            data6 = obj['data6']
            data7 = obj['data7']
            data8 = obj['data8']
            data9 = obj['data9']
            data10 = obj['data10']
            data11 = obj['data11']
            data12 = obj['data12']

            w.write(excel_row, 0, index, style)
            w.write(excel_row, 1, classesLevel, style)
            w.write(excel_row, 2, professionName, style)
            w.write(excel_row, 3, classesName, style)
            w.write(excel_row, 4, studentCode, style)
            w.write(excel_row, 5, studentName, style)
            w.write(excel_row, 6, studentSex, style)
            w.write(excel_row, 7, studentPhone, style)
            w.write(excel_row, 8, employmentStatus, style)
            w.write(excel_row, 9, companyName, style)
            w.write(excel_row, 10, companyAddress, style)
            w.write(excel_row, 11, postName, style)
            w.write(excel_row, 12, studentSalary, style)
            w.write(excel_row, 13, companyPhone, style)
            w.write(excel_row, 14, teacherName, style)
            w.write(excel_row, 15, teacherPhone, style)
            w.write(excel_row, 16, studentStatus, style)
            w.write(excel_row, 17, addTime, style)

            w.write(excel_row, 18, data1, style if data1 == '本月无变动' else myStyle)
            w.write(excel_row, 19, data2, style if data2 == '本月无变动' else myStyle)
            w.write(excel_row, 20, data3, style if data3 == '本月无变动' else myStyle)
            w.write(excel_row, 21, data4, style if data4 == '本月无变动' else myStyle)
            w.write(excel_row, 22, data5, style if data5 == '本月无变动' else myStyle)
            w.write(excel_row, 23, data6, style if data6 == '本月无变动' else myStyle)
            w.write(excel_row, 24, data7, style if data7 == '本月无变动' else myStyle)
            w.write(excel_row, 25, data8, style if data8 == '本月无变动' else myStyle)
            w.write(excel_row, 26, data9, style if data9 == '本月无变动' else myStyle)
            w.write(excel_row, 27, data10, style if data10 == '本月无变动' else myStyle)
            w.write(excel_row, 28, data11, style if data11 == '本月无变动' else myStyle)
            w.write(excel_row, 29, data12, style if data12 == '本月无变动' else myStyle)
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
