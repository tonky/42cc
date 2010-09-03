from django.db import models


class Bio(models.Model):
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=30, blank=True)
    born = models.DateField()
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)

    def __unicode__(self):
        return self.name


class Log(models.Model):
    method = models.CharField(max_length=10)
    url = models.URLField(verify_exists=False)
    date = models.DateTimeField(auto_now_add=True)


class CrudLog(models.Model):
    action = models.CharField(max_length=10)
    model = models.CharField(max_length=20)
    date = models.DateTimeField(auto_now_add=True)
