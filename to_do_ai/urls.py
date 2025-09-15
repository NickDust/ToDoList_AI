from django.urls import path
from . import views

urlpatterns = [
    path("tasks/", views.TaskView.as_view(), name="task"),
    path("ai/", views.TaskAIView.as_view(), name="ai-task"),
    path("tasks/<int:pk>/", views.DetailTaskView.as_view(), name="task-delete"),
    path("register/", views.RegisterView.as_view(), name="register")
]