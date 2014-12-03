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