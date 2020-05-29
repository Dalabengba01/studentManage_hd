from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import enterpriseManage, enterprisePost, postBindentErprise, studentManage


def addEnterprise(requestData):
    """
    添加企业
    :param requestData:
    :return:
    """
    enterpriseName = requestData['enterpriseName']
    enterpriseScale = requestData['enterpriseScale']
    enterpriseContacts = requestData['enterpriseContacts']
    enterprisePhone = requestData['enterprisePhone']
    enterpriseAddress = requestData['enterpriseAddress']
    skyEyeScore = requestData['skyEyeScore']
    remarks = requestData['remarks']

    if enterpriseManage.objects.filter(enterpriseName=enterpriseName).values():
        return JsonResponse({'ret': 1, 'data': '已有相同名称企业,请重命名！'})
    else:
        index = 1000
        # 正序查询
        dataList = list(enterpriseManage.objects.values().order_by('enterpriseCode'))
        if len(dataList) <= 0:
            index = 1000
        else:
            index = int(dataList[-1]['enterpriseCode']) + 1
        if enterpriseManage.objects.create(enterpriseCode=index, enterpriseName=enterpriseName,
                                           enterpriseScale=enterpriseScale, enterpriseContacts=enterpriseContacts,
                                           enterprisePhone=enterprisePhone, enterpriseAddress=enterpriseAddress,
                                           skyEyeScore=skyEyeScore, remarks=remarks):
            return JsonResponse({'ret': 0, 'data': '添加企业成功！'})
        else:
            return JsonResponse({'ret': 1, 'data': '添加企业失败,请稍后重试！'})


def editEnterprise(requestData):
    """
    编辑企业
    :param requestData:
    :return:
    """
    enterpriseName = requestData['enterpriseName']
    enterpriseScale = requestData['enterpriseScale']
    enterpriseContacts = requestData['enterpriseContacts']
    enterprisePhone = requestData['enterprisePhone']
    enterpriseAddress = requestData['enterpriseAddress']
    skyEyeScore = requestData['skyEyeScore']
    remarks = requestData['remarks']
    if enterpriseManage.objects.filter(enterpriseName=enterpriseName).update(enterpriseName=enterpriseName,
                                                                             enterpriseScale=enterpriseScale,
                                                                             enterpriseContacts=enterpriseContacts,
                                                                             enterprisePhone=enterprisePhone,
                                                                             enterpriseAddress=enterpriseAddress,
                                                                             skyEyeScore=skyEyeScore, remarks=remarks):
        return JsonResponse({'ret': 0, 'data': '修改企业信息成功！'})
    else:
        return JsonResponse({'ret': 1, 'data': '修改企业信息失败,请稍后重试！'})


def getEnterpriseData(requestData):
    """
    获取企业数据
    :param requestData:
    :return:
    """
    keyWord = requestData['keyWord']  # 查询的关键词
    pageNum = requestData['pageNum']  # 当前页数
    pageSize = requestData['pageSize']  # 一页多少数据

    if keyWord == '':
        enterpriseData = list(enterpriseManage.objects.values())
    else:
        enterpriseData = list(enterpriseManage.objects.filter(enterpriseName__contains=keyWord).values())

    # 更新该企业有多少岗位
    enterpriseList = []
    for i in enterpriseData:
        i.update({'postCount': postBindentErprise.objects.filter(enterpriseCode=i['enterpriseCode']).count()})
        enterpriseList.append(i)

    paginator = Paginator(enterpriseList, pageSize)  # 每页显示多少数据
    total = paginator.count  # 总数据量
    data = paginator.page(pageNum).object_list  # 某一页的数据

    return JsonResponse({
        'ret': 0,
        'data': data,
        'pageNum': pageNum,
        'total': total,
    })


def deleteEnterprise(requestData):
    """
    删除企业操作
    :param requestData:
    :return:
    """
    enterpriseCode = str(requestData['enterpriseCode'])
    # 获取本企业所有岗位
    postCode = [i['postCode'] for i in list(postBindentErprise.objects.filter(enterpriseCode=enterpriseCode).values())
                if str(i['enterpriseCode']) == enterpriseCode]
    try:
        enterpriseManage.objects.filter(enterpriseCode=enterpriseCode).delete()
        for i in postCode:
            postBindentErprise.objects.filter(postCode=i).delete()
            enterprisePost.objects.filter(postCode=i).delete()
            studentManage.objects.filter(postCode=i).update(postCode='0', enterpriseCode='0', employmentStatus='待安置',
                                                            studentSalary=0)
        return JsonResponse({'ret': 0, 'data': '删除企业成功！'})
    except Exception:
        return JsonResponse({'ret': 0, 'data': '删除企业失败，请稍后重试！'})


def getEnterpriseDataCascaderOptions(requestData):
    """
    岗位创建界面获取企业联级菜单数据
    :param requestData:
    :return:
    """
    enterpriseData = list(enterpriseManage.objects.values())
    return JsonResponse({'ret': 0, 'data': enterpriseData})


def addPost(requestData):
    """
    添加岗位
    :param requestData:
    :return:
    """
    postName = requestData['postName']
    recruitCount = requestData['recruitCount']
    postAddress = requestData['postAddress']
    salaryTreatment = requestData['salaryTreatment']
    bindEnterprise = requestData['bindEnterprise'][0]

    # 1.企业岗位数据库写入岗位数据
    index = 1000
    # 正序查询
    dataList = list(enterprisePost.objects.values().order_by('postCode'))
    if len(dataList) <= 0:
        index = 1000
    else:
        index = int(dataList[-1]['postCode']) + 1
    if enterprisePost.objects.create(postCode=index, postName=postName, recruitCount=recruitCount,
                                     postAddress=postAddress,
                                     salaryTreatment=salaryTreatment) \
            and postBindentErprise.objects.create(postCode=index, enterpriseCode=bindEnterprise):
        return JsonResponse({'ret': 0, 'data': '添加岗位成功！'})
    else:
        return JsonResponse({'ret': 1, 'data': '添加岗位失败,请稍后重试！'})


def editPost(requestData):
    """
    编辑岗位
    :param requestData:
    :return:
    """
    postCode = requestData['postCode']
    postName = requestData['postName']
    recruitCount = requestData['recruitCount']
    postAddress = requestData['postAddress']
    salaryTreatment = requestData['salaryTreatment']
    bindEnterprise = requestData['bindEnterprise']

    if enterprisePost.objects.filter(postCode=postCode).update(postName=postName, recruitCount=recruitCount,
                                                               postAddress=postAddress,
                                                               salaryTreatment=salaryTreatment) and postBindentErprise.objects.filter(
        postCode=postCode).update(enterpriseCode=bindEnterprise):
        return JsonResponse({'ret': 0, 'data': '编辑岗位成功！'})
    else:
        return JsonResponse({'ret': 1, 'data': '编辑岗位失败,请稍后重试！'})


def deletePost(requestData):
    """
    删除岗位操作
    :param requestData:
    :return:
    """
    postCode = requestData['postCode']
    if enterprisePost.objects.filter(postCode=postCode).delete() and postBindentErprise.objects.filter(
            postCode=postCode).delete() and studentManage.objects.filter(postCode=postCode).update(enterpriseCode='0',
                                                                                                   postCode='0',
                                                                                                   employmentStatus='待安置',
                                                                                                   studentSalary=0):
        return JsonResponse({'ret': 0, 'data': '删除岗位成功！'})
    else:
        return JsonResponse({'ret': 1, 'data': '删除岗位失败,请稍后重试！'})


def getPostData(requestData):
    """
    获取岗位数据
    :param requestData:
    :return:
    """
    keyWord = requestData['keyWord']  # 查询的关键词
    pageNum = requestData['pageNum']  # 当前页数
    pageSize = requestData['pageSize']  # 一页多少数据
    queryType = requestData['queryType']  # 查询类型

    postData = []
    if keyWord != '' and queryType == 'postName':
        postData = list(enterprisePost.objects.filter(postName__contains=keyWord).values())
    else:
        postData = list(enterprisePost.objects.filter().values())

    # 获取该岗位属于哪个公司toEnterprise
    postDataList = []
    for i in postData:
        for ii in list(enterpriseManage.objects.filter(
                enterpriseCode=list(postBindentErprise.objects.filter(postCode=i['postCode']).values())[0][
                    'enterpriseCode']).values()):
            i.update({'toEnterprise': ii['enterpriseName']})
            break
        postDataList.append(i)
    paginator = Paginator(postDataList, pageSize)  # 每页显示多少数据

    if keyWord != '' and queryType == 'enterpriseName':
        postDataList1 = []
        for i in postDataList:
            if keyWord in i['toEnterprise']:
                postDataList1.append(i)
        paginator = Paginator(postDataList1, pageSize)  # 每页显示多少数据

    total = paginator.count  # 总数据量
    data = paginator.page(pageNum).object_list  # 某一页的数据

    return JsonResponse({
        'ret': 0,
        'data': data,
        'pageNum': pageNum,
        'total': total,
    })


def getPostDataCascaderOptions(requestData):
    """
    获取岗位联级菜单数据
    :param requestData:
    :return:
    """
    # 合成企业数据
    enterpriseData = []  # 临时存放企业数据
    for i in enterpriseManage.objects.values():
        enterpriseCode = i['enterpriseCode']
        enterpriseName = i['enterpriseName']
        enterpriseData.append({'value': str(enterpriseCode), 'label': enterpriseName, 'disabled': True})

    # 提取绑定关系数据
    bindData = []
    for i in list(postBindentErprise.objects.values()):
        for ii in list(enterprisePost.objects.values()):
            if str(i['postCode']) == str(ii['postCode']):
                postCode = ii['postCode']
                postName = ii['postName']
                enterpriseCode = i['enterpriseCode']
                bindData.append(
                    {'value': str(postCode), 'label': postName, 'enterpriseCode': str(enterpriseCode)})

    # # 合成岗位数据
    postData = []
    for i in enterpriseData:
        childrenData = []
        for ii in bindData:
            postCode = ii['value']
            postName = ii['label']
            if i['value'] == ii['enterpriseCode']:
                childrenData.append({'value': str(postCode), 'label': postName})
        postData.append({'enterpriseCode': i['value'], 'children': childrenData})

    # 合成最终数据
    enterpriseContainer = []  # 企业容器包含岗位子容器 value:企业编号 label:企业名称
    for i in enterpriseData:
        for ii in bindData:
            if i['value'] == ii['enterpriseCode']:
                i['disabled'] = False
                for iii in postData:
                    if iii['enterpriseCode'] == ii['enterpriseCode']:
                        i.update({'children': iii['children']})
        enterpriseContainer.append(i)
    return JsonResponse({'ret': 0, 'data': enterpriseContainer})
