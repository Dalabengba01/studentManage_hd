import os

from django.http import StreamingHttpResponse, JsonResponse
from xlwt import *

from .models import studentManage, professionManage, classesManage, enterprisePost, enterpriseManage


def getexportStudentData(request):
    """
    导出学生数据为Excel表格(学生数据=基本数据+已就业数据|未就业数据)
    :param request: 包含用户请求的参数
    :return: 返回文件流对象
    """
    searchType = request['getDataType']

    # 创建新的列表供后续功能操作
    subData0 = []

    obj = studentManage.objects

    if searchType in ['全部', '参军', '待安置', '已安置', '拟升学']:

        if searchType == '全部':
            subData0 = list(obj.filter().values())

        if searchType == '参军':
            subData0 = list(obj.filter(employmentStatus='参军').values())

        if searchType == '待安置':
            subData0 = list(obj.filter(employmentStatus='待安置').values())

        if searchType == '已安置':
            subData0 = list(obj.filter(employmentStatus='已安置').values())

        if searchType == '拟升学':
            subData0 = list(obj.filter(employmentStatus='拟升学').values())

    userList = []
    for i in subData0:
        # 获取所属专业,班级名称，班级届数并合并到学生信息列表中
        for ii in obj.filter(studentCode=i['studentCode']).values():
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
        for studentBindData in list(obj.filter(studentCode=i['studentCode']).values()):
            if studentBindData['postCode'] != '0':
                for postData in list(enterprisePost.objects.filter(postCode=studentBindData['postCode']).values()):
                    i.update({'postName': postData['postName'], 'postAddress': postData['postAddress']})
            else:
                i.update({'postName': '未绑定', 'postAddress': '未绑定'})

            if studentBindData['enterpriseCode'] != '0':
                for enterpriseData in list(
                        enterpriseManage.objects.filter(enterpriseCode=studentBindData['enterpriseCode']).values()):
                    i.update({'enterpriseName': enterpriseData['enterpriseName'],
                              'enterpriseAddress': enterpriseData['enterpriseAddress'],
                              'enterprisePhone': enterpriseData['enterprisePhone']})
            else:
                i.update({'enterpriseName': '未绑定', 'enterpriseAddress': '未绑定', 'enterprisePhone': '未绑定'})
        userList.append(i)

    # {
    #     'studentCode': '30317217',
    #     'studentName': '方言',
    #     'studentSex': '男生',
    #     'studentNativePlace': '陕西省-安康市',
    #     'studentPhone': '11111111111',
    #     'employmentStatus': '已安置',
    #     'studentSalary': 3000,
    #     'teacherName': '王斌',
    #     'teacherPhone': '11111111111',
    #     'studentStatus': '良好',
    #     'postCode': '1003',
    #     'enterpriseCode': '1002',
    #     'postDuty': '软件测试',
    #     'professionCode': '1000',
    #     'classesCode': '1000',
    #     'remarks': '1',
    #     'addTime': datetime.datetime(),
    #     'studentLevel': '2018',
    #     'toProfession': '云计算技术与运用',
    #     'toClasses': '云算3182',
    #     'postName': '软件测试',
    #     'postAddress': '新疆维吾尔自治区-阿勒泰地区',
    #     'enterpriseName': '飞象互娱科技',
    #     'enterpriseAddress': '新疆维吾尔自治区阿勒泰',
    #     'enterprisePhone': '01085518557'
    # }

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
        w.write(1, 1, "学生学号", style)
        w.write(1, 2, "学生姓名", style)
        w.write(1, 3, "学生性别", style)
        w.write(1, 4, "学生届数", style)
        w.write(1, 5, "所属专业", style)
        w.write(1, 6, "所属班级", style)
        w.write(1, 7, "学生籍贯", style)
        w.write(1, 8, "学生电话", style)
        w.write(1, 9, "就业状态", style)
        w.write(1, 10, "企业名称", style)
        w.write(1, 11, "企业地址", style)
        w.write(1, 12, "企业电话", style)
        w.write(1, 13, "岗位名称", style)
        w.write(1, 14, "工作地址", style)
        w.write(1, 15, "最新薪资", style)
        w.write(1, 16, "直属主管", style)
        w.write(1, 17, "主管电话", style)
        w.write(1, 18, "学生状态", style)
        w.write(1, 19, "修改时间", style)

        # 写入数据(第一行是标题，第二行表头，第三行开始写数据)
        excel_row = 2

        w.write_merge(0, 0, 0, 12, excelTitle, style1)
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
            studentSalary = obj['studentSalary']
            teacherName = obj['teacherName']
            teacherPhone = obj['teacherPhone']
            studentStatus = obj['studentStatus']
            addTime = obj['addTime'].strftime("%Y-%m-%d %H:%M:%S")[:19]

            w.write(excel_row, 0, index, style)
            w.write(excel_row, 1, studentCode, style)
            w.write(excel_row, 2, studentName, style)
            w.write(excel_row, 3, studentSex, style)
            w.write(excel_row, 4, studentLevel, style)
            w.write(excel_row, 5, toProfession, style)
            w.write(excel_row, 6, toClasses, style)
            w.write(excel_row, 7, studentNativePlace, style)
            w.write(excel_row, 8, studentPhone, style)
            w.write(excel_row, 9, employmentStatus, style)
            w.write(excel_row, 10, enterpriseName, style)
            w.write(excel_row, 11, enterpriseAddress, style)
            w.write(excel_row, 12, enterprisePhone, style)
            w.write(excel_row, 13, postName, style)
            w.write(excel_row, 14, postAddress, style)
            w.write(excel_row, 15, studentSalary, style)
            w.write(excel_row, 16, teacherName, style)
            w.write(excel_row, 17, teacherPhone, style)
            w.write(excel_row, 18, studentStatus, style)
            w.write(excel_row, 19, addTime, style)

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
