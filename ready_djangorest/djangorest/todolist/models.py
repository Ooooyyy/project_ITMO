from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import ast

class LoggedInMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class Tag(models.Model):
    tag = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return "{}".format(self.tag)

class Tasklist(models.Model):
    name = models.CharField(max_length=200)
    friends = models.ManyToManyField(User, related_name='tasklists')
    ro_friends = models.ManyToManyField(User, related_name='tasklists_ro')
    owner = models.ForeignKey('auth.User', related_name='owner', on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.name)


class Task(models.Model):
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(max_length=1000, blank=True)
    completed = models.BooleanField(default=False)
    date_created = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    date_modified = models.DateField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name='tasks')

    PRIORITY = (
        ('h', 'High'),
        ('m', 'Medium'),
        ('l', 'Low'),
        ('n', 'None')
    )

    priority = models.CharField(max_length=1, choices=PRIORITY, default='n')
    tasklist = models.ForeignKey(Tasklist, related_name='tasks', on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.name)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=10)
