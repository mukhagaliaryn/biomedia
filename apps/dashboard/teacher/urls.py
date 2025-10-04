from django.urls import path
from . import views


urlpatterns = [
    path('', views.teacher_view, name='teacher'),
    path('subject/<subject_id>/', views.subject_manage_view, name='subject_manage'),
]