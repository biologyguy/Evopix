from evp.models import Evopix
from django.db import models


# Create your models here.
class LandTypes(models.Model):
    type_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=40)
    base_color = models.CharField(max_length=6)


class FenceTypes(models.Model):
    fence_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)
    description = models.TextField()


class LandUnit(models.Model):
    land_id = models.AutoField(primary_key=True)
    x = models.IntegerField()
    y = models.IntegerField()
    type = models.ForeignKey(LandTypes)
    evopic = models.ForeignKey(Evopix, null=True)
    l_fence = models.ForeignKey('FenceTypes', related_name='FenceTypesL', null=True)
    r_fence = models.ForeignKey('FenceTypes', related_name='FenceTypesR', null=True)
    t_fence = models.ForeignKey('FenceTypes', related_name='FenceTypesT', null=True)
    b_fence = models.ForeignKey('FenceTypes', related_name='FenceTypesB', null=True)

    class Meta:
        unique_together = ('x', 'y',)


