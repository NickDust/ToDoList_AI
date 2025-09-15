from django.db import models
from django.contrib.auth.models import User

class UserProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class TaskModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User", null=True, blank=True)
    task = models.CharField(max_length=50, blank=False)
    description = models.CharField(max_length=250, blank=True)
    due_date = models.DateField(null=True, blank=True)
    prioprity = models.PositiveSmallIntegerField(choices= {1: "Low", 2: "Medium", 3: "High"}, default=2)
    completed = models.BooleanField(default=False)
    time_task_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task