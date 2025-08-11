from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import UserSubject, UserChapter, UserLesson, Task, UserTask, UserVideo, UserWritten, UserTextGap, \
    UserAnswer
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

    user_lessons_qs = UserLesson.objects.filter(user_subject=user_subject)
    user_chapters = UserChapter.objects.filter(user_subject=user_subject)

    user_lessons_by_chapter = {}
    for ul in user_lessons_qs:
        chapter_id = ul.lesson.chapter_id
        user_lessons_by_chapter.setdefault(chapter_id, []).append(ul)

    if request.method == 'POST':
        tasks = Task.objects.filter(lesson=user_lesson.lesson)
        for task in tasks:
            user_task, created = UserTask.objects.get_or_create(user_lesson=user_lesson, task=task)

            if task.task_type == 'video':
                for video in task.videos.all():
                    UserVideo.objects.create(user_task=user_task, video=video)

            elif task.task_type == 'written':
                for written in task.written.all():
                    UserWritten.objects.create(user_task=user_task, written=written)

            elif task.task_type == 'text_gap':
                for text_gap in task.text_gaps.all():
                    UserTextGap.objects.create(user_task=user_task, text_gap=text_gap)

            elif task.task_type == 'test':
                for question in task.questions.all():
                    UserAnswer.objects.create(user_task=user_task, option=question)

    context = {
        'user_subject': user_subject,
        'user_chapter': user_chapter,
        'user_lesson': user_lesson,
        'user_chapters': user_chapters,
        'user_lessons_by_chapter': user_lessons_by_chapter,
    }

    return render(request, 'app/dashboard/student/user/subject/chapter/lesson/page.html', context)
