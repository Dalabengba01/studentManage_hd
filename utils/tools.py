def getIndex(model, field):
    """
    用于数据创建时主键ID的获取及起始值设定
    :param model: model类
    :param field: 按照某个字段排序
    :return: 返回计算后的index
    """
    index = 1000
    # 正序查询
    dataList = list(model.objects.values().order_by(field))
    if len(dataList) <= 0:
        index = 1000
    else:
        index = int(dataList[-1][field]) + 1
    return index


# def listSplit(data, pageSize, pageNum):
#     """
#     用于数据创建时主键ID的获取及起始值设定
#     :param data: 所有数据列表
#     :param pageSize: 一页多少数据
#     :param pageNum: 当前页数
#     :return: 返回数据
#     """
#     totalData = len(data)  # 总数据数
#     totalPage = (totalData + pageSize - 1) / pageSize  # 总页数
#     start = (pageNum - 1) * pageSize  # 当前数据起始索引
#     end = start + pageSize if start + pageSize <= totalData else totalData
#     currentData = data[start:end]  # 当前页数据
#     return {'totalData': totalData, 'totalPage': totalPage, 'currentData': currentData}
#
#
# if __name__ == '__main__':
#     a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 1, 1, 1, 1, 1, 1, 1, 5, 6, 7, 8, 'a', 'd', 'fs', 2, 11]
#     z = listSplit(a, 5, 7)
#     print(z)
