from rest_framework import serializers
from .models import TaskModel
from django.contrib.auth.models import User

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskModel
        fields = "__all__"

class AiTaskSerializer(serializers.Serializer):
    text = serializers.CharField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    