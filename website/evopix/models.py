from django.db import models


# Create your models here.
class Evopic(models.Model):
    id = models.BigIntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=40, null=True)
    parent1 = models.BigIntegerField()
    parent2 = models.BigIntegerField()
    evp = models.TextField()
    zeroed_evp = models.TextField()
    hype_score = models.PositiveIntegerField()
    health = models.SmallIntegerField()
    birthday = models.DateTimeField(auto_now_add=True)
