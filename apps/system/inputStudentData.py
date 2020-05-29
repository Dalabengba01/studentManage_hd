import os

from django.http import JsonResponse
import xlrd

from .models import studentManage, professionManage, classesManage


def inputStudentData():
    """
    导入学生Excel表格数据
    :param request: 包含用户请求的参数
    :return:
    """
    try:
        book = xlrd.open_workbook(os.path.join('static/', 'inputStudentData.xlsx'))
    except FileNotFoundError:
        book = xlrd.open_workbook(os.path.join('static/', 'inputStudentData.xls'))

    sheet1 = book.sheets()[0]

    # 获取第一行数据判断是否为合格文件
    isTrue = sheet1.row_values(0)[0].find('中兴创新学院学生就业管理系统', 0)
    if isTrue != -1:
        # 合格文件，可以进行分析
        nrows = sheet1.nrows
        ncols = sheet1.ncols

        # 获取学生数据
        studentDataList = []
        for i in range(2, nrows):
            container = []
            for ii in range(1, ncols):
                container.append(sheet1.cell(i, ii).value)
            studentDataList.append(container)

        keys = ['classesLevel', 'professionName', 'classesName', 'studentCode', 'studentName', 'studentSex',
                'studentPhone', 'employmentStatus', 'companyName', 'companyAddress', 'postName', 'studentSalary',
                'companyPhone', 'teacherName', 'teacherPhone', 'studentStatus', 'addTime', 'data1', 'data2', 'data3',
                'data4', 'data5', 'data6', 'data7', 'data8', 'data9', 'data10', 'data11', 'data12']
        # 动态生成字典
        studentList = {}
        for values in studentDataList:
            for k, v in zip(keys, values):
                studentList[k] = v

        # 数据分析及数据导入数据库
        # 0.分析此学生是否存在数据库(是否覆盖原有信息)
        # 1.分析此学生属于那个班级，专业
        # 2.操作学生基本信息数据表还原基本信息
        # 3.操作学生与专业班级的数据库恢复依赖关系

    else:
        return JsonResponse({'ret': 1, 'data': '此文件不合法!'})

    return JsonResponse({'ret': 0, 'data': '上传文件成功!'})
