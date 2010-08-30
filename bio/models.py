from django.db import models

class Bio(models.Model):
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=30)
    bio = models.TextField()
    email = models.EmailField()


class MwareRequest(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    url = models.URLField(verify_exists=False)
