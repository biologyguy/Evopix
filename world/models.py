from evp.models import Evopix
from the_shop.models import Fences
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class LandTypes(models.Model):
    type_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=40)
    base_color = models.CharField(max_length=6)


class LandUnit(models.Model):
    land_id = models.AutoField(primary_key=True)
    x = models.IntegerField()
    y = models.IntegerField()
    type = models.ForeignKey(LandTypes)
    evopic = models.ForeignKey(Evopix, null=True)
    l_fence = models.ForeignKey('the_shop.Fences', related_name='FenceTypesL', null=True)
    r_fence = models.ForeignKey('the_shop.Fences', related_name='FenceTypesR', null=True)
    t_fence = models.ForeignKey('the_shop.Fences', related_name='FenceTypesT', null=True)
    b_fence = models.ForeignKey('the_shop.Fences', related_name='FenceTypesB', null=True)
    user = models.ForeignKey(User, null=True)

    class Meta:
        unique_together = ('x', 'y',)


class UserInfo(models.Model):
    user = models.ForeignKey(User)
    farm_midpoint = models.ForeignKey(LandUnit)
    virtual_cash = models.IntegerField(default=0)