from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import enterpriseManage, enterprisePost, studentManage
from utils.tools import getIndex, listSplit


def addEnterprise(requestData):
    """
    添加企业
    :param requestData:
    :return:
    """
    enterpriseName = requestData['enterpriseName']
    enterpriseScale = requestData['enterpriseScale']
    goodGrade = requestData['goodGrade']
    enterpriseContacts = requestData['enterpriseContacts']
    enterprisePhone = requestData['enterprisePhone']
    enterpriseAddress = requestData['enterpriseAddress']
    skyEyeScore = requestData['skyEyeScore']
    remarks = requestData['remarks']

    if enterpriseManage.objects.filter(enterpriseName=enterpriseName).values():
        return JsonResponse({'ret': 1, 'data': '已有相同名称企业,请重命名！'})
    else:
        index = getIndex(enterpriseManage, 'enterpriseCode')
        if enterpriseManage.objects.create(enterpriseCode=index, enterpriseName=enterpriseName,
                                           enterpriseScale=enterpriseScale,
                                           goodGrade=goodGrade,
                                           enterpriseContacts=enterpriseContacts,
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
    goodGrade = requestData['goodGrade']
    enterpriseContacts = requestData['enterpriseContacts']
    enterprisePhone = requestData['enterprisePhone']
    enterpriseAddress = requestData['enterpriseAddress']
    skyEyeScore = requestData['skyEyeScore']
    remarks = requestData['remarks']
    if enterpriseManage.objects.filter(enterpriseName=enterpriseName).update(enterpriseName=enterpriseName,
                                                                             enterpriseScale=enterpriseScale,
                                                                             goodGrade=goodGrade,
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
        enterpriseData = list(enterpriseManage.objects.filter(isDelete=False).values())
    else:
        enterpriseData = list(
            enterpriseManage.objects.filter(enterpriseName__contains=keyWord, isDelete=False).values())

    # 更新该企业有多少岗位
    enterpriseList = []
    for i in enterpriseData:
        i.update(
            {'postCount': enterprisePost.objects.filter(enterpriseCode=i['enterpriseCode'], isDelete=False).count()})
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
    postCode = [i['postCode'] for i in list(enterprisePost.objects.filter(enterpriseCode=enterpriseCode).values())
                if str(i['enterpriseCode']) == enterpriseCode]
    try:
        enterpriseManage.objects.filter(enterpriseCode=enterpriseCode).update(isDelete=True)
        for i in postCode:
            enterprisePost.objects.filter(postCode=i).update(isDelete=True)
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
    enterpriseData = list(enterpriseManage.objects.filter(isDelete=False).values())
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
    index = getIndex(enterprisePost, 'postCode')
    if enterprisePost.objects.create(postCode=index, postName=postName, recruitCount=recruitCount,
                                     postAddress=postAddress,
                                     salaryTreatment=salaryTreatment, enterpriseCode=bindEnterprise):
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
                                                               salaryTreatment=salaryTreatment,
                                                               enterpriseCode=bindEnterprise):
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
    if enterprisePost.objects.filter(postCode=postCode).update(isDelete=True) and studentManage.objects.filter(
            postCode=postCode).update(enterpriseCode='0',
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

    myData = []
    p_obj = enterprisePost.objects
    # 没搜索条件时
    posts = list(p_obj.filter(isDelete=False).values())

    # 岗位属性筛选
    if queryType in ['postName'] and keyWord != '':
        posts = list(p_obj.filter(postName__icontains=keyWord, isDelete=False).values())
        posts = listSplit(posts, pageSize, pageNum)['currentData']

    # 数据合成
    for post in posts:
        for enterprise in enterpriseManage.objects.filter(enterpriseCode=post['enterpriseCode'],
                                                          isDelete=False).values():
            post.update({'toEnterprise': enterprise['enterpriseName']})
        myData.append(post)
    myData = listSplit(myData, pageSize, pageNum)
    # 岗位属性筛选
    if queryType in ['enterpriseName'] and keyWord != '':
        myData = [i for i in myData if
                  i['toEnterprise' if queryType == 'enterpriseName' else queryType].lower().find(keyWord.lower()) != -1]
        myData = listSplit(myData, pageSize, pageNum)

    return JsonResponse({
        'ret': 0,
        'data': myData['currentData'],
        'pageNum': pageNum,
        'total': myData['dataSum'],
    })


def getPostDataCascaderOptions(requestData):
    """
    获取岗位联级菜单数据
    :param requestData:
    :return:
    """
    enterpriseContainer = []
    for enterprise in enterpriseManage.objects.filter(isDelete=False).values():
        zz = {'value': enterprise['enterpriseCode'], 'label': enterprise['enterpriseName'], 'disabled': True,
              'children': []}
        postList = []
        for post in enterprisePost.objects.filter(enterpriseCode=enterprise['enterpriseCode'], isDelete=False).values():
            postList.append({'value': post['postCode'], 'label': post['postName']})
        zz.update({'disabled': False, 'children': postList})
        enterpriseContainer.append(zz)

    return JsonResponse({'ret': 0, 'data': enterpriseContainer})
