from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import UserSubject, UserChapter, UserLesson
from core.utils.decorators import role_required


# User lesson page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
@role_required('student')
def user_lesson_view(request, subject_id, chapter_id, lesson_id):
    user = request.user

    user_subject = get_object_or_404(UserSubject, user=user, pk=subject_id)
    user_chapter = get_object_or_404(UserChapter, user_subject=user_subject, pk=chapter_id)
    user_lesson = get_object_or_404(UserLesson, user_subject=user_subject, pk=lesson_id)

    user_lessons_qs = UserLesson.objects.select_related('lesson').filter(user_subject=user_subject)
    user_chapters = user_subject.user_chapters.select_related('chapter').prefetch_related(
        'chapter__lessons'
    )
    user_lessons_by_chapter = {}
    for ul in user_lessons_qs:
        chapter_id = ul.lesson.chapter_id
        user_lessons_by_chapter.setdefault(chapter_id, []).append(ul)

    context = {
        'user_subject': user_subject,
        'user_chapter': user_chapter,
        'user_lesson': user_lesson,
        'user_chapters': user_chapters,
        'user_lessons_by_chapter': user_lessons_by_chapter,
    }

    return render(request, 'app/dashboard/student/user/subject/chapter/lesson/page.html', context)
