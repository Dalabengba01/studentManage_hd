from django.db import models


class BaseModels(models.Model):
    """模型类自定义抽象基类"""

    class Meta:
        abstract = True

    isDelete = models.BooleanField(verbose_name='是否删除', default=False)


class teacherData(models.Model):
    """系统初始化的教师管理账户"""

    class Meta:
        verbose_name = '教师基本信息'
        verbose_name_plural = verbose_name

    user_name = models.CharField('账户名称', max_length=21, primary_key=True)
    user_pass = models.CharField('账户密码', max_length=21)
    teacher_name = models.CharField('教师名称', max_length=10)
    is_login = models.BooleanField('是否登录', default=False)
    is_super = models.BooleanField('超级管理员', default=False)
    add_time = models.DateField(auto_now_add=True, verbose_name="初始化时间")


class enterpriseManage(BaseModels):
    """企业管理相关数据"""

    class Meta:
        verbose_name = '企业管理相关数据'
        verbose_name_plural = verbose_name

    enterpriseCode = models.IntegerField('企业编号', primary_key=True)
    enterpriseName = models.CharField('企业名称', max_length=30)
    enterpriseScale = models.CharField('企业规模', max_length=300)
    enterpriseContacts = models.CharField('企业联系人', max_length=30)
    enterprisePhone = models.CharField('企业电话', max_length=100)
    enterpriseAddress = models.CharField('企业地址', max_length=400)
    skyEyeScore = models.CharField('天眼查分值', max_length=8)
    goodGrade = models.CharField('优良等级', max_length=30)
    remarks = models.CharField('备注', max_length=400)
    addTime = models.DateField(auto_now=True, verbose_name="更新日期")


class enterprisePost(BaseModels):
    """企业岗位表"""

    class Meta:
        verbose_name = '企业岗位表'
        verbose_name_plural = verbose_name

    postCode = models.CharField('岗位编号', max_length=30, primary_key=True)
    postName = models.CharField('岗位名称', max_length=200)
    recruitCount = models.CharField('招聘人数', max_length=30)
    postAddress = models.CharField('工作地点', max_length=30)
    salaryTreatment = models.CharField('工资待遇', max_length=400)
    enterpriseCode = models.CharField('企业编号', max_length=30)
    addTime = models.DateField(auto_now_add=True, verbose_name="创建时间")


class professionManage(BaseModels):
    """后台--专业管理相关数据"""

    class Meta:
        verbose_name = '专业管理相关数据'
        verbose_name_plural = verbose_name

    professionCode = models.CharField('专业编号', max_length=30, primary_key=True)
    professionName = models.CharField('专业名称', max_length=21)
    addTime = models.DateField(auto_now_add=True, verbose_name="创建时间")


class classesManage(BaseModels):
    """后台--班级管理相关数据"""

    class Meta:
        verbose_name = '班级管理相关数据'
        verbose_name_plural = verbose_name

    classesCode = models.CharField('班级编号', max_length=30, primary_key=True)
    classesLevel = models.CharField('班级届数', max_length=21)
    classesName = models.CharField('班级名称', max_length=21)
    professionCode = models.CharField('专业编号', max_length=30)
    addTime = models.DateField(auto_now_add=True, verbose_name="创建时间")


class studentManage(BaseModels):
    """学生相关数据"""

    class Meta:
        verbose_name = '学生相关数据'
        verbose_name_plural = verbose_name

    studentCode = models.CharField('学生学号', primary_key=True, max_length=30)
    studentName = models.CharField('学生名称', max_length=30)
    studentSex = models.CharField('学生性别', max_length=10)
    studentNativePlace = models.CharField('学生籍贯', max_length=30)
    studentPhone = models.CharField('学生电话', max_length=11)
    employmentStatus = models.CharField('就业状态', max_length=21)
    studentSalary = models.IntegerField('实习薪资')
    teacherName = models.CharField('直属主管', max_length=30)
    teacherPhone = models.CharField('主管电话', max_length=11)
    studentStatus = models.CharField('学生状态', max_length=10)
    updateTeacherName = models.CharField('更新教师', max_length=30)
    # 学生绑定企业岗位
    postCode = models.CharField('岗位编号', max_length=30)
    enterpriseCode = models.CharField('企业编号', max_length=30)
    postDuty = models.CharField('岗位职责', max_length=400)
    # 学生绑定专业班级
    professionCode = models.CharField('专业编号', max_length=30)
    classesCode = models.CharField('班级编号', max_length=30)
    remarks = models.CharField('备注', max_length=400)
    addTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")


class studentPostTrack(BaseModels):
    """学生岗位追踪表"""
    trackCode = models.IntegerField('数据编号', primary_key=True)
    studentCode = models.CharField('学生学号', max_length=30)
    studentName = models.CharField('学生名称', max_length=30)
    recordTeacher = models.CharField('记录教师', max_length=30)
    enterpriseName = models.CharField('企业名称', max_length=30)
    postName = models.CharField('岗位名称', max_length=200)
    postDuty = models.CharField('岗位职责', max_length=400)
    studentSalary = models.IntegerField('实习薪资')
    remarks = models.CharField('备注', max_length=400)
    addTime = models.DateTimeField(auto_now_add=True, verbose_name="修改时间")


class systemLogs(models.Model):
    """系统操作日志"""

    class Meta:
        verbose_name = '系统操作日志'
        verbose_name_plural = verbose_name

    logCode = models.CharField('日志编号', max_length=30, primary_key=True)
    operationUser = models.CharField('操作账户', max_length=30)
    operationType = models.CharField('操作类型', max_length=100)
    dataRecord = models.TextField('数据记录', max_length=2000)
    addTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")


class editLocked(models.Model):
    """信息编辑锁记录"""

    class Meta:
        verbose_name = '信息编辑锁记录'
        verbose_name_plural = verbose_name

    lockedCode = models.IntegerField('编辑锁编号', primary_key=True)
    userAction = models.CharField('用户活动', max_length=30)
    userName = models.CharField('用户名称', max_length=30)
    code = models.IntegerField('数据标识')  # 可以是学号，专业编号等
    lockedTime = models.DateTimeField(auto_now=True, verbose_name="锁定时间")
