from django.shortcuts import redirect


def default(request):
    """
    默认首页重定向
    如果存在管理用户跳转到管理员登录界面，不存在就跳转初始化
    :param request:
    :return:
    """
    return redirect('index.html')