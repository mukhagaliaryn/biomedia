from django.urls import path
from .views import home, course


urlpatterns = [
    path('', home.home_view, name='home'),
    path('subjects/', home.subjects_view, name='subjects'),
    path('subjects/<pk>/', home.subject_detail_view, name='subject_detail'),
    path('user/subject/<subject_id>/chapter/<chapter_id>/lesson/<lesson_id>/', course.user_course_view, name='user_course'),

    # handlers...
    path('subjects/enroll/<int:subject_id>/', home.enroll_subject_handler, name='enroll_subject'),
]
