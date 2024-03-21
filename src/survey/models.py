from django.db import models


class Survey(models.Model):
    title = models.CharField("заголовок", max_length=256)
    execution_time = models.IntegerField()
