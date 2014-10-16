from django.db import models
from evp.models import *


# Create your models here.
class LandUnit(models.Model):
    land_id = models.AutoField(primary_key=True)
    x = models.IntegerField()
    y = models.IntegerField()
    type = models.ForeignKey(LandTypes)
    left_fence = models.ForeignKey(FenceTypes)
    evopic = models.ForeignKey(Evopix)

    class Meta:
        unique_together = ('x', 'y',)


class LandTypes(models.Model):
    type_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=40)
    base_color = models.CharField(max_length=6)


class FenceTypes(models.Model):
    fence_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)
    description = models.TextField()