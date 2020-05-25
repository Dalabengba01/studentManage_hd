from django.db import models

class teacherData(models.Model):
    """系统初始化的教师管理账户"""

    class Meta:
        verbose_name = '教师基本信息'
        verbose_name_plural = verbose_name

    user_name = models.CharField('账户名称', max_length=21)
    user_pass = models.CharField('账户密码', max_length=21)
    is_login = models.BooleanField('是否登录', default=False)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="初始化时间")


class professionManage(models.Model):
    """后台--专业管理相关数据"""

    class Meta:
        verbose_name = '专业管理相关数据'
        verbose_name_plural = verbose_name

    professionCode = models.AutoField('专业编码', primary_key=True)
    professionName = models.CharField('专业名称', max_length=21)
    addTime = models.DateField(auto_now_add=True, verbose_name="创建时间")


class classesManage(models.Model):
    """后台--班级管理相关数据"""

    class Meta:
        verbose_name = '班级管理相关数据'
        verbose_name_plural = verbose_name

    classesCode = models.AutoField('班级编号', primary_key=True)
    classesLevel = models.CharField('班级届数', max_length=21)
    classesName = models.CharField('班级名称', max_length=21)
    addTime = models.DateField(auto_now_add=True, verbose_name="创建时间")


class studentManage(models.Model):
    """学生相关数据"""

    class Meta:
        verbose_name = '学生相关数据'
        verbose_name_plural = verbose_name

    studentCode = models.CharField('学生学号', primary_key=True, max_length=30)
    studentName = models.CharField('学生名称', max_length=21)
    studentSex = models.CharField('学生性别', max_length=10)
    studentPhone = models.CharField('学生电话', max_length=11)
    employmentStatus = models.CharField('就业状态', max_length=21)
    companyName = models.CharField('单位名称', max_length=30)
    companyAddress = models.CharField('单位地址', max_length=30)
    postName = models.CharField('岗位名称', max_length=30)
    studentSalary = models.CharField('实习薪资', max_length=20)
    companyPhone = models.CharField('实习单位电话', max_length=11)
    teacherName = models.CharField('指导老师姓名', max_length=30)
    teacherPhone = models.CharField('指导老师电话', max_length=11)
    studentStatus = models.CharField('学生状态', max_length=10)
    addTime = models.DateField(auto_now_add=True, verbose_name="创建时间")


class employmentReturnVisit(models.Model):
    """学生就业状态(每月1更)"""

    class Meta:
        verbose_name = '学生就业状态'
        verbose_name_plural = verbose_name

    statusID = models.IntegerField('就业状态标识', primary_key=True)
    studentCode = models.CharField('学生学号', max_length=30)
    data1 = models.CharField('1月回访记录', max_length=300, default='本月无变动')
    data2 = models.CharField('2月回访记录', max_length=300, default='本月无变动')
    data3 = models.CharField('3月回访记录', max_length=300, default='本月无变动')
    data4 = models.CharField('4月回访记录', max_length=300, default='本月无变动')
    data5 = models.CharField('5月回访记录', max_length=300, default='本月无变动')
    data6 = models.CharField('6月回访记录', max_length=300, default='本月无变动')
    data7 = models.CharField('7月回访记录', max_length=300, default='本月无变动')
    data8 = models.CharField('8月回访记录', max_length=300, default='本月无变动')
    data9 = models.CharField('9月回访记录', max_length=300, default='本月无变动')
    data10 = models.CharField('10月回访记录', max_length=300, default='本月无变动')
    data11 = models.CharField('11月回访记录', max_length=300, default='本月无变动')
    data12 = models.CharField('12月回访记录', max_length=300, default='本月无变动')
    addTime = models.DateField(auto_now_add=True, verbose_name="创建时间")


class classesBindProfession(models.Model):
    """班级绑定专业"""

    class Meta:
        verbose_name = '班级绑定专业相关数据'
        verbose_name_plural = verbose_name

    classesCode = models.AutoField('班级编号', primary_key=True)
    professionCode = models.CharField('专业编号', max_length=21)
    addTime = models.DateField(auto_now_add=True, verbose_name="创建时间")


class studentBindClassesAndProfession(models.Model):
    """学生绑定容器(专业和班级)"""

    class Meta:
        verbose_name = '学生绑定容器相关数据'
        verbose_name_plural = verbose_name

    studentCode = models.AutoField('学生学号', primary_key=True)
    professionCode = models.CharField('专业编码', max_length=20)
    classesCode = models.CharField('班级编号', max_length=20)
