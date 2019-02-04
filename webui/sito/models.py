from django.db import models

class Community(models.Model):
    id_backend = models.IntegerField(unique=True)
    name = models.CharField(max_length=1024)

    class Meta:
        verbose_name_plural = 'communities'
