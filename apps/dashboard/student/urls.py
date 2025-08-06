from django.urls import path
from .views import home, subject


urlpatterns = [
    path('', home.student_view, name='student'),
    path('subject/<pk>/', home.subject_detail_view, name='subject_detail'),
    path('subject/enroll/<int:subject_id>/', home.enroll_user_to_subject, name='enroll_subject'),

    path('user/subject/<subject_id>/chapter/<chapter_id>/lesson/<lesson_id>/', subject.user_lesson_view, name='user_lesson'),
]
