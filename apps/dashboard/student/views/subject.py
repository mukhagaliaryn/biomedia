from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.models import UserSubject, UserChapter, UserLesson, UserTask, UserVideo, UserWritten, UserTextGap, \
    UserAnswer, UserMatching
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

    user_lessons_qs = UserLesson.objects.filter(user_subject=user_subject).order_by('lesson__order')
    user_chapters = UserChapter.objects.filter(user_subject=user_subject).order_by('chapter__order')

    user_lessons_by_chapter = {}
    for ul in user_lessons_qs:
        chapter_id = ul.lesson.chapter_id
        user_lessons_by_chapter.setdefault(chapter_id, []).append(ul)

    first_task = (
        UserTask.objects
        .filter(user_lesson=user_lesson)
        .select_related('task')
        .order_by('task__order')
        .first()
    )

    context = {
        'user_subject': user_subject,
        'user_chapter': user_chapter,
        'user_lesson': user_lesson,
        'user_chapters': user_chapters,
        'user_lessons_by_chapter': user_lessons_by_chapter,
        'first_task': first_task
    }

    return render(request, 'app/dashboard/student/user/subject/chapter/lesson/page.html', context)


@login_required
@role_required('student')
def lesson_start_handler(request, subject_id, chapter_id, lesson_id):
    user = request.user
    user_subject = get_object_or_404(UserSubject, user=user, pk=subject_id)
    user_chapter = get_object_or_404(UserChapter, user_subject=user_subject, pk=chapter_id)
    user_lesson = get_object_or_404(UserLesson, user_subject=user_subject, pk=lesson_id)

    if request.method != 'POST':
        return redirect('user_lesson', subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id)

    if not user_lesson.lesson.tasks.exists():
        messages.warning(request, 'Бұл сабақта ешқандай тапсырма жоқ!')
        return redirect('user_lesson', subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id)

    for task in user_lesson.lesson.tasks.all():
        user_task, created = UserTask.objects.get_or_create(
            user_lesson=user_lesson,
            task=task
        )

        if task.task_type == 'video':
            for video in task.videos.all():
                UserVideo.objects.get_or_create(
                    user_task=user_task,
                    video=video
                )

        elif task.task_type == 'written':
            for written in task.written.all():
                UserWritten.objects.get_or_create(
                    user_task=user_task,
                    written=written,
                )

        elif task.task_type == 'text_gap':
            for text_gap in task.text_gaps.all():
                UserTextGap.objects.get_or_create(
                    user_task=user_task,
                    text_gap=text_gap,
                )

        elif task.task_type == 'test':
            for question in task.questions.all():
                ua, created = UserAnswer.objects.get_or_create(
                    user_task=user_task,
                    question=question
                )
                ua.options.set([])

        elif task.task_type == 'matching':
            for pair in task.matching_pairs.all():
                UserMatching.objects.get_or_create(
                    user_task=user_task,
                    pair=pair,
                    selected_right='',
                    is_correct=False
                )

    user_lesson.status = 'in-progress'
    user_lesson.save()

    first_user_task = (
        user_lesson.user_tasks
        .select_related('task')
        .order_by('task__order')
        .first()
    )

    if first_user_task:
        messages.success(request, 'Сабақ басталды!')
        return redirect(
            'user_lesson_task',
            subject_id=subject_id,
            chapter_id=chapter_id,
            lesson_id=lesson_id,
            task_id=first_user_task.id
        )

    return redirect('user_lesson', subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id)


# User lesson page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
@role_required('student')
def user_lesson_task_view(request, subject_id, chapter_id, lesson_id, task_id):
    user = request.user
    user_subject = get_object_or_404(UserSubject, user=user, pk=subject_id)
    user_chapter = get_object_or_404(UserChapter, user_subject=user_subject, pk=chapter_id)
    user_lesson = get_object_or_404(UserLesson, user_subject=user_subject, pk=lesson_id)
    user_task = get_object_or_404(UserTask, pk=task_id)

    user_tasks = UserTask.objects.filter(user_lesson=user_lesson)

    context = {
        'user_subject': user_subject,
        'user_chapter': user_chapter,
        'user_lesson': user_lesson,
        'user_task': user_task,

        'user_tasks': user_tasks
    }

    return render(request, 'app/dashboard/student/user/subject/chapter/lesson/task/page.html', context)