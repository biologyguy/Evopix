from django.db import models


# Create your models here.
class BreedingPellets(models.Model):
    pellet_id = models.AutoField(primary_key=True)
    type = models.TextField()
    description = models.TextField()
    path_split = models.FloatField()
    point_split = models.FloatField()
    del_point = models.FloatField()
    point_move = models.FloatField()
    gradient_param = models.FloatField()
    stop_split = models.FloatField()
    del_stop = models.FloatField()
    stop_params = models.FloatField()
    stroke_color = models.FloatField()
    stroke_width = models.FloatField()
    stroke_opacity = models.FloatField()
    base_price = models.IntegerField()


class GrassSeed(models.Model):
    seed_id = models.AutoField(primary_key=True)
    color = models.CharField(max_length=6)
    svg = models.TextField()
    base_price = models.IntegerField()


class Fences(models.Model):
    fence_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)
    description = models.TextField()
    horiz_img_location = models.TextField()
    vert_img_location = models.TextField()
    base_price = models.IntegerField()