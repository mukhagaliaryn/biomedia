from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# User course page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def user_course_view(request, subject_id, chapter_id, lesson_id):
    return render(request, 'app/user/subject/chapter/lesson/page.html', {})