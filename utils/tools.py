def getIndex(model, field):
    """
    用于数据创建时主键ID的获取及起始值设定
    :param model: model类
    :param field: 按照某个字段排序
    :return: 返回计算后的index
    """
    dataList = list(model.objects.values().order_by(field))
    if len(dataList) <= 0:
        index = 1000
    else:
        index = int(dataList[-1][field]) + 1
    return index


def listSplit(data, pageSize, pageNum):
    """
    用于自定义数据提前分页(提高系统性能)
    :param data: 所有数据列表
    :param pageSize: 一页多少数据
    :param pageNum: 当前页数
    :return: 返回数据分页字典
    """
    dataSum = len(data)  # 总数据数
    pageSum = (dataSum + pageSize - 1) / pageSize  # 总页数
    startIndex = (pageNum - 1) * pageSize  # 当前起始索引
    end = startIndex + pageSize
    endIndex = end if end <= dataSum else dataSum  # 当前结束索引
    currentData = data[startIndex:endIndex]  # 当前页数据
    return {'dataSum': dataSum, 'pageSum': pageSum, 'currentData': currentData}

# if __name__ == '__main__':
#     a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 1, 1, 1, 1, 1, 1, 1, 5, 6, 7, 8, 'a', 'd', 'fs', 2, 11]
#     z = listSplit(a, 5, 7)
#     print(z)
