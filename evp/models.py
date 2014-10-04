from django.db import models


# Create your models here.
class Evopix(models.Model):
    evo_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40, null=True)
    parent1 = models.BigIntegerField()
    parent2 = models.BigIntegerField()
    evp = models.TextField()
    zeroed_evp = models.TextField()
    hype_score = models.IntegerField()
    health = models.IntegerField()
    birthday = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.evo_id


class Paths(models.Model):
    path_id = models.AutoField(primary_key=True)
    parent_path = models.BigIntegerField()
    parent_evopic = models.ForeignKey(Evopix)
    birthday = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.path_id


class Points(models.Model):
    point_id = models.AutoField(primary_key=True)
    parent_point = models.BigIntegerField()
    parent_path = models.ForeignKey(Paths)
    parent_evopic = models.ForeignKey(Evopix)
    birthday = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.point_id


class Stops(models.Model):
    stop_id = models.AutoField(primary_key=True)
    parent_stop = models.BigIntegerField()
    parent_path = models.ForeignKey(Paths)
    parent_evopic = models.ForeignKey(Evopix)
    birthday = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.stop_id