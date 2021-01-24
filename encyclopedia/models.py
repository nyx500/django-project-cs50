from django.db import models

class Hidden(models.Model):
    name = models.CharField(max_length=255)