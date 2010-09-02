from django.db import models


class Bio(models.Model):
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=30)
    bio = models.TextField()
    email = models.EmailField()

    def __unicode__(self):
        return self.name


class Log(models.Model):
    method = models.CharField(max_length=10)
    url = models.URLField(verify_exists=False)
    date = models.DateTimeField(auto_now_add=True)
