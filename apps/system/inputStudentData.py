import os
from django.http import JsonResponse
import xlrd

from utils.tools import getIndex
from .models import professionManage, classesManage, enterpriseManage, enterprisePost, studentManage


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
    sheets = book.sheets()
    try:
        isTrue = sheets[0].row_values(0)[0].find('中兴创新学院学生就业管理系统', 0) != -1
    except IndexError:
        isTrue = False
    if len(sheets) == 3 and isTrue:
        # 文件合法则开始解析
        ################# 1.首先获取专业及班级数据并入库 #################
        nrows = sheets[1].nrows
        ncols = sheets[1].ncols

        getKeypro = {
            1: 'professionName',
            2: 'classesLevel',
            3: 'classesName'
        }

        professionDataList = []
        for i in range(2, nrows):
            container = {}
            for ii in range(1, ncols):
                container.update({getKeypro[ii]: str(sheets[1].cell(i, ii).value)})
            professionDataList.append(container)
        # 创建专业及班级
        profession_obj = professionManage.objects
        classes_obj = classesManage.objects
        for i in professionDataList:
            # 判断此专业是否存在，不存在则创建，否则更新
            if profession_obj.filter(professionName=i['professionName']).count() > 0:
                profession_obj.filter(professionName=i['professionName']).update(
                    professionName=i['professionName'], isDelete=False)
            else:
                profession_obj.create(professionName=i['professionName'],
                                      professionCode=getIndex(professionManage, 'professionCode'))

            # 创建班级
            if classes_obj.filter(classesName=i['classesName'], isDelete=False).count() > 0:
                classes_obj.filter(classesName=i['classesName'], isDelete=False).update(
                    classesName=i['classesName'], isDelete=False)
            else:
                professionCode = \
                    list(profession_obj.filter(professionName=i['professionName']).values_list('professionCode'))[0][0]
                if i['classesLevel'] != '' or i['classesName'] != '':
                    classes_obj.create(classesCode=getIndex(classesManage, 'classesCode'), classesName=i['classesName'],
                                       classesLevel=str(i['classesLevel']).split('.')[0],
                                       professionCode=professionCode)

        ################# 2.其次获取企业及岗位数据并入库 #################
        nrows = sheets[2].nrows
        ncols = sheets[2].ncols

        getKeyent = {
            1: 'enterpriseName',
            2: 'enterpriseScale',
            3: 'goodGrade',
            4: 'enterpriseContacts',
            5: 'enterprisePhone',
            6: 'enterpriseAddress',
            7: 'remarks',
            8: 'skyEyeScore',
            9: 'postName',
            10: 'postAddress',
            11: 'salaryTreatment',
            12: 'recruitCount'
        }

        enterpriseDataList = []
        for i in range(2, nrows):
            container = {}
            for ii in range(1, ncols):
                container.update({getKeyent[ii]: str(sheets[2].cell(i, ii).value)})
            enterpriseDataList.append(container)

        enterprise_obj = enterpriseManage.objects
        post_obj = enterprisePost.objects
        for i in enterpriseDataList:
            # 先创建企业再创建岗位
            if enterprise_obj.filter(enterpriseName=i['enterpriseName'], isDelete=False).count() > 0:
                enterprise_obj.filter(enterpriseName=i['enterpriseName'], isDelete=False).update(
                    enterpriseName=i['enterpriseName'], enterpriseScale=i['enterpriseScale'], goodGrade=i['goodGrade'],
                    enterpriseContacts=i['enterpriseContacts'], enterprisePhone=i['enterprisePhone'],
                    enterpriseAddress=i['enterpriseAddress'], skyEyeScore=i['skyEyeScore'], remarks=i['remarks'], isDelete=False)
            else:
                enterprise_obj.create(
                    enterpriseCode=getIndex(enterpriseManage, 'enterpriseCode'),
                    enterpriseName=i['enterpriseName'], enterpriseScale=i['enterpriseScale'], goodGrade=i['goodGrade'],
                    enterpriseContacts=i['enterpriseContacts'], enterprisePhone=i['enterprisePhone'],
                    enterpriseAddress=i['enterpriseAddress'], skyEyeScore=i['skyEyeScore'], remarks=i['remarks'])

            # 创建岗位
            enterpriseCode = \
                list(enterprise_obj.filter(enterpriseName=i['enterpriseName']).values_list('enterpriseCode'))[0][0]
            if post_obj.filter(postName=i['postName'], enterpriseCode=enterpriseCode,
                               isDelete=False).count() > 0:
                post_obj.filter(postName=i['postName'],
                                isDelete=False).update(
                    postName=i['postName'], recruitCount=str(i['recruitCount']).split('.')[0],
                    postAddress=i['postAddress'],
                    salaryTreatment=i['salaryTreatment'], isDelete=False)
            else:
                if i['postName'] != '' or i['salaryTreatment'] != '' or i['postAddress'] != '':
                    post_obj.create(
                        postCode=getIndex(enterprisePost, 'postCode'),
                        postName=i['postName'], recruitCount=str(i['recruitCount']).split('.')[0],
                        postAddress=i['postAddress'],
                        salaryTreatment=i['salaryTreatment'], enterpriseCode=enterpriseCode)

        ################# 3.最后获取学生数据并入库 #################
        nrows = sheets[0].nrows
        ncols = sheets[0].ncols

        getKeypro = {
            1: 'studentCode',
            2: 'studentName',
            3: 'studentSex',
            4: 'studentLevel',
            5: 'toProfession',
            6: 'toClasses',
            7: 'studentNativePlace',
            8: 'studentPhone',
            9: 'employmentStatus',
            10: 'enterpriseName',
            11: 'enterpriseAddress',
            12: 'enterprisePhone',
            13: 'postName',
            14: 'postAddress',
            15: 'postDuty',
            16: 'studentSalary',
            17: 'teacherName',
            18: 'teacherPhone',
            19: 'updateTeacherName',
            20: 'studentStatus',
            21: 'remarks',
            22: 'addTime'
        }

        studentDataList = []
        for i in range(2, nrows):
            container = {}
            for ii in range(1, ncols):
                container.update({getKeypro[ii]: str(sheets[0].cell(i, ii).value)})
                studentDataList.append(container)

        student_obj = studentManage.objects
        profession_obj = professionManage.objects
        classes_obj = classesManage.objects
        enterprise_obj = enterpriseManage.objects
        post_obj = enterprisePost.objects
        for i in studentDataList:
            if student_obj.filter(studentCode=str(i['studentCode']).split('.')[0]).count() > 0:
                professionCode = '0' if i['toProfession'] == '未绑定' else \
                    list(profession_obj.filter(professionName=i['toProfession']).values_list('professionCode'))[0][0]
                classesCode = '0' if i['toClasses'] == '未绑定' else \
                    list(classes_obj.filter(professionCode=professionCode, classesName=i['toClasses']).values_list('classesCode'))[0][0]
                enterpriseCode = '0' if i['enterpriseName'] == '未绑定' else \
                    list(enterprise_obj.filter(enterpriseName=i['enterpriseName']).values_list('enterpriseCode'))[0][0]
                postCode = '0' if i['postName'] == '未绑定' else \
                    list(post_obj.filter(enterpriseCode=enterpriseCode, postName=i['postName']).values_list('postCode'))[0][0]
                student_obj.filter(studentCode=str(i['studentCode']).split('.')[0]).update(
                    studentCode=str(i['studentCode']).split('.')[0], studentName=i['studentName'],
                    studentSex=i['studentSex'], studentNativePlace=i['studentNativePlace'],
                    studentPhone=i['studentPhone'], employmentStatus=i['employmentStatus'],
                    studentSalary=str(i['studentSalary']).split('.')[0], teacherName=i['teacherName'],
                    teacherPhone=i['teacherPhone'], studentStatus=i['studentStatus'],
                    updateTeacherName=i['updateTeacherName'], postCode=postCode, enterpriseCode=enterpriseCode,
                    postDuty=i['postDuty'], professionCode=professionCode, classesCode=classesCode,
                    remarks=i['remarks'], isDelete=False)
            else:
                professionCode = '0' if i['toProfession'] == '未绑定' else \
                    list(profession_obj.filter(professionName=i['toProfession']).values_list('professionCode'))[0][0]
                classesCode = '0' if i['toClasses'] == '未绑定' else \
                    list(classes_obj.filter(professionCode=professionCode, classesName=i['toClasses']).values_list('classesCode'))[0][0]
                enterpriseCode = '0' if i['enterpriseName'] == '未绑定' else \
                    list(enterprise_obj.filter(enterpriseName=i['enterpriseName']).values_list('enterpriseCode'))[0][0]
                postCode = '0' if i['postName'] == '未绑定' else \
                    list(post_obj.filter(enterpriseCode=enterpriseCode, postName=i['postName']).values_list('postCode'))[0][0]
                student_obj.create(
                    studentCode=str(i['studentCode']).split('.')[0], studentName=i['studentName'],
                    studentSex=i['studentSex'], studentNativePlace=i['studentNativePlace'],
                    studentPhone=i['studentPhone'], employmentStatus=i['employmentStatus'],
                    studentSalary=str(i['studentSalary']).split('.')[0], teacherName=i['teacherName'],
                    teacherPhone=i['teacherPhone'], studentStatus=i['studentStatus'],
                    updateTeacherName=i['updateTeacherName'], postCode=postCode, enterpriseCode=enterpriseCode,
                    postDuty=i['postDuty'], professionCode=professionCode, classesCode=classesCode,
                    remarks=i['remarks'])
    else:
        return JsonResponse({'ret': 1, 'data': '此文件不合法，请按照特定的表格格式上传!'})

    return JsonResponse({'ret': 0, 'data': '文件数据处理成功!'})
