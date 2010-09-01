from django.db import models


class Bio(models.Model):
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=30)
    bio = models.TextField()
    email = models.EmailField()
