from django.db import models


'''自关联字段的外键指向自身，所以models.ForeignKey('self')

使用related_name指明父级查询子级数据的语法

默认Area模型类对象.area_set语法

related_name='subs'现在Area模型类对象.subs语法'''


class Area(models.Model):
    """省市区"""

    name = models.CharField(max_length=20, verbose_name='名称')

    parent = models.ForeignKey('self',
                               on_delete=models.SET_NULL,
                               related_name='subs',
                               null=True,
                               blank=True,
                               verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '省市区'
        verbose_name_plural = '省市区'

    def __str__(self):
        return self.name