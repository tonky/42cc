from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
import sys


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


def log_save(sender, **kwargs):
    if sender == CrudLog:  # we don't need no bad recursion
        return

    action = "update"

    if kwargs['created']:
        action = "create"

    cl = CrudLog(model=sender.__name__, action=action)
    cl.save()


def log_delete(sender, **kwargs):
    cl = CrudLog(model=sender.__name__, action="delete")
    cl.save()


post_save.connect(log_save)
post_delete.connect(log_delete)
