import json
from django.http import JsonResponse
from .models import teacherData, systemLogs
from . import profession, classes, student, enterprise, system, dataStatistics, exportStudentData, inputStudentData


# 用户基础功能函数
def user(request):
    """
    系统用户接口（负责用户登录，注册，注销，修改密码等。。。）
    将请求参数统一放入request 的 params 属性中，方便后续处理
    :param request:
    :return:
    """

    # GET请求 参数在url中，通过request 对象的 GET属性获取
    global requestData
    if request.method == 'GET':
        request.params = request.GET

    # POST/PUT/DELETE 请求 参数 从 request 对象的 body 属性中获取
    elif request.method in ['POST', 'PUT', 'DELETE']:

        # 根据接口，POST/PUT/DELETE 请求的消息体都是 json格式
        requestData = json.loads(request.body)

    # 根据不同的action分派给不同的函数进行处理
    useraction = requestData['useraction']

    # 这几个功能无需登陆
    if useraction == 'systemInit':
        return system.systemInit(requestData)

    if useraction == 'isSystemInit':
        return system.isSystemInit(requestData)

    if useraction == 'isLogin':
        return system.isLogin(requestData)

    if useraction == 'userLogin':
        return system.userLogin(requestData)

    # 以下功能需要验证是否登录了才可以操作
    for i in teacherData.objects.filter(user_name=requestData['username']).values():
        if i['is_login']:

            # 使用日志收集
            system.logs(requestData)

            if useraction == 'userLogout':
                return system.userLogout(requestData)

            if useraction == 'userModifyPass':
                return system.userModifyPass(requestData)

            if useraction == 'userModifyAccount':
                return system.userModifyAccount(requestData)

            if useraction == 'userModifyTeacher':
                return system.userModifyTeacher(requestData)

        else:
            return JsonResponse({'ret': 1, 'data': '用户未登录！'})
    else:
        return JsonResponse({'ret': 1, 'data': '原始账号名称错误！'})


# 用户扩展功能函数
def data(request):
    """
    系统数据接口（负责获取学生信息，就业信息等。。。。）
    将请求参数统一放入request 的 params 属性中，方便后续处理
    :param request:
    :return:
    """

    # GET请求 参数在url中，通过request 对象的 GET属性获取
    if request.method == 'GET':
        request.params = request.GET

    # POST/PUT/DELETE 请求 参数 从 request 对象的 body 属性中获取
    elif request.method in ['POST', 'PUT', 'DELETE']:
        myFile = request.FILES.get("file", None)  # 获取上传的文件，如果没有文件，则默认为None
        if not myFile:
            # 根据接口，POST/PUT/DELETE 请求的消息体都是 json格式
            requestData = json.loads(request.body)
            # 根据不同的action分派给不同的函数进行处理
            useraction = requestData['useraction']
            for i in teacherData.objects.filter(user_name=requestData['username']).values():
                if i['is_login']:

                    # 使用日志收集
                    system.logs(requestData)

                    if useraction == 'addProfession':
                        return profession.addProfession(requestData)

                    if useraction == 'editProfession':
                        return profession.editProfession(requestData)

                    if useraction == 'deleteProfession':
                        return profession.deleteProfession(requestData)

                    if useraction == 'getProfessionData':
                        return profession.getProfessionData(requestData)

                    if useraction == 'addClasses':
                        return classes.addClasses(requestData)

                    if useraction == 'editClasses':
                        return classes.editClasses(requestData)

                    if useraction == 'deleteClasses':
                        return classes.deleteClasses(requestData)

                    if useraction == 'getclassesData':
                        return classes.getclassesData(requestData)

                    if useraction == 'getProfessionDataCascaderOptions':
                        return classes.getProfessionDataCascaderOptions(requestData)

                    if useraction == 'getProfessionAndClassesDataCascaderOptions':
                        return classes.getProfessionAndClassesDataCascaderOptions(requestData)

                    if useraction == 'getProfessionAndClassesCascaderOptions':
                        return student.getProfessionAndClassesCascaderOptions(requestData)

                    if useraction == 'getProfessionAndClassesLevelDataCascaderOptions':
                        return classes.getProfessionAndClassesLevelDataCascaderOptions(requestData)

                    if useraction == 'addstudent':
                        return student.addstudent(requestData)

                    if useraction == 'editStudent':
                        return student.editStudent(requestData)

                    if useraction == 'deleteStudent':
                        return student.deleteStudent(requestData)

                    if useraction == 'getStudentData':
                        return student.getStudentData(requestData)

                    if useraction == 'getPostTrackData':
                        return student.getPostTrackData(requestData)

                    if useraction == 'deletePostTrack':
                        return student.deletePostTrack(requestData)

                    if useraction == 'addEnterprise':
                        return enterprise.addEnterprise(requestData)

                    if useraction == 'editEnterprise':
                        return enterprise.editEnterprise(requestData)

                    if useraction == 'getEnterpriseData':
                        return enterprise.getEnterpriseData(requestData)

                    if useraction == 'deleteEnterprise':
                        return enterprise.deleteEnterprise(requestData)

                    if useraction == 'getEnterpriseDataCascaderOptions':
                        return enterprise.getEnterpriseDataCascaderOptions(requestData)

                    if useraction == 'addPost':
                        return enterprise.addPost(requestData)

                    if useraction == 'editPost':
                        return enterprise.editPost(requestData)

                    if useraction == 'deletePost':
                        return enterprise.deletePost(requestData)

                    if useraction == 'getPostData':
                        return enterprise.getPostData(requestData)

                    if useraction == 'getPostDataCascaderOptions':
                        return enterprise.getPostDataCascaderOptions(requestData)

                    if useraction == 'getWorkAreaData':
                        return dataStatistics.getWorkAreaData(requestData)

                    if useraction == 'getUnemployedRateData':
                        return dataStatistics.getUnemployedRateData(requestData)

                    if useraction == 'getSalaryData':
                        return dataStatistics.getSalaryData(requestData)

                    if useraction == 'getPeopleData':
                        return dataStatistics.getPeopleData(requestData)

                    if useraction == 'getIndexData':
                        return dataStatistics.getIndexData(requestData)

                    if useraction == 'exportStudentData':
                        return exportStudentData.getexportStudentData(requestData)

                    if useraction == 'getWorkDirection':
                        return dataStatistics.getWorkDirection(requestData)

                    if useraction == 'getSystemLogsData':
                        return system.getSystemLogsData(requestData)

                    if useraction == 'deleteSystemLogsData':
                        return system.deleteSystemLogsData(requestData)

                    if useraction == 'systemEditLocked':
                        return system.systemEditLocked(requestData)

                    if useraction == 'systemDataRecovery':
                        return system.systemDataRecovery(requestData)

                else:
                    return JsonResponse({'ret': 1, 'data': '用户未登录！'})
        else:
            import os
            lastName = myFile.name.split('.')[1]
            destination = open(os.path.join('static/', 'inputStudentData.' + lastName), 'wb+')  # 打开特定的文件进行二进制的写操作
            for chunk in myFile.chunks():  # 分块写入文件
                destination.write(chunk)
            destination.close()
            return inputStudentData.inputStudentData()
