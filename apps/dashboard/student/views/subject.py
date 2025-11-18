from django.db.models.aggregates import Avg
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from apps.dashboard.student.services.subject import handle_post_request, get_related_data
from core.models import UserSubject, UserChapter, UserLesson, UserTask, UserVideo, UserWritten, UserTextGap, \
    UserAnswer, UserMatchingAnswer, Lesson, UserTableAnswer, Feedback
from core.utils.decorators import role_required


# user_lesson page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
@role_required('student')
def user_lesson_view(request, subject_id, chapter_id, lesson_id):
    user = request.user
    user_subject = get_object_or_404(UserSubject, user=user, pk=subject_id)
    user_lesson = get_object_or_404(UserLesson, user_subject=user_subject, pk=lesson_id)
    user_chapter = get_object_or_404(UserChapter, user_subject=user_subject, chapter=user_lesson.lesson.chapter)
    tasks = user_lesson.lesson.tasks.exclude(task_type='video')
    user_lessons_qs = UserLesson.objects.filter(user_subject=user_subject).order_by('lesson__order')

    # ------------------ link for user tasks ------------------
    first_task = (
        UserTask.objects.filter(user_lesson=user_lesson).select_related('task').order_by('task__order').first()
    )

    # ------------------ prev, next links ------------------
    previous_lesson = None
    next_lesson = None

    lesson_list = list(user_lessons_qs)
    try:
        current_index = lesson_list.index(user_lesson)
        if current_index > 0:
            previous_lesson = lesson_list[current_index - 1]
        if current_index < len(lesson_list) - 1:
            next_lesson = lesson_list[current_index + 1]
    except ValueError:
        pass

    # ------------------ for navbar ------------------
    user_chapters = UserChapter.objects.filter(user_subject=user_subject).order_by('chapter__order')
    user_lessons_by_chapter = {}
    for ul in user_lessons_qs:
        chapter_id = ul.lesson.chapter_id
        lesson_tasks = ul.lesson.tasks.all()
        total_duration = sum(task.duration for task in lesson_tasks)
        ul.total_duration = total_duration
        user_lessons_by_chapter.setdefault(chapter_id, []).append(ul)

    context = {
        'user_subject': user_subject,
        'user_chapter': user_chapter,
        'user_lesson': user_lesson,
        'tasks': tasks,
        'first_task': first_task,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'total_duration': sum(task.duration for task in user_lesson.lesson.tasks.all()),
        'user_chapters': user_chapters,
        'user_lessons_by_chapter': user_lessons_by_chapter,
        'active_chapter_id': user_chapter.pk,
    }

    return render(request, 'app/dashboard/student/user/subject/chapter/lesson/page.html', context)


# actions
# ----------------------------------------------------------------------------------------------------------------------
# start lesson
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
                UserVideo.objects.get_or_create(user_task=user_task, video=video)

        elif task.task_type == 'written':
            for written in task.written.all():
                UserWritten.objects.get_or_create(user_task=user_task, written=written)

        elif task.task_type == 'text_gap':
            for text_gap in task.text_gaps.all():
                UserTextGap.objects.get_or_create(user_task=user_task, text_gap=text_gap)

        elif task.task_type == 'test':
            for question in task.questions.all():
                ua, created = UserAnswer.objects.get_or_create(user_task=user_task, question=question)
                ua.options.set([])

        elif task.task_type == 'matching':
            for column in task.columns.all():
                for item in column.correct_items.all():
                    UserMatchingAnswer.objects.get_or_create(user_task=user_task, item=item)

        elif task.task_type == 'table':
            rows = task.table_rows.all()
            columns = task.table_columns.all()
            for row in rows:
                for column in columns:
                    UserTableAnswer.objects.get_or_create(user_task=user_task, row=row, column=column)

    user_lesson.status = 'in-progress'
    user_lesson.started_at = timezone.now()
    user_lesson.save()

    first_user_task = user_lesson.user_tasks.select_related('task').order_by('task__order').first()

    if first_user_task:
        messages.success(request, 'Сабақ басталды!')
        return redirect(
            'user_lesson_task',
            subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id, task_id=first_user_task.id
        )

    return redirect('user_lesson', subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id)


# finish lesson
@login_required
@role_required('student')
@require_POST
def lesson_finish_handler(request, subject_id, chapter_id, lesson_id):
    user = request.user

    user_subject = get_object_or_404(UserSubject, user=user, pk=subject_id)
    user_chapter = get_object_or_404(UserChapter, user_subject=user_subject, pk=chapter_id)
    user_lesson = get_object_or_404(UserLesson, user_subject=user_subject, pk=lesson_id)
    lesson = user_lesson.lesson
    user_tasks = UserTask.objects.filter(user_lesson=user_lesson)

    if user_lesson.is_completed:
        return redirect('user_lesson', subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id)

    # ---------------- Lesson type: lesson ----------------
    if lesson.lesson_type == 'lesson':
        total_rating = user_tasks.aggregate(total=Sum('rating')).get('total', 0)
        user_lesson.rating = total_rating
        user_lesson.percentage = int(round(user_lesson.rating * 10))

    # ---------------- Lesson type: chapter ----------------
    elif lesson.lesson_type == 'chapter':
        user_rating = user_tasks.aggregate(total=Sum('rating'))['total'] or 0
        max_rating = lesson.tasks.aggregate(total=Sum('rating'))['total'] or 0

        print(user_rating)
        print(max_rating)
        user_lesson.rating = user_rating
        user_lesson.percentage = round((user_rating / max_rating) * 100, 2)
        chapter_lessons = UserLesson.objects.filter(
            user_subject=user_subject,
            lesson__chapter=lesson.chapter,
            lesson__lesson_type='lesson'
        )

        avg_rating = chapter_lessons.aggregate(avg=Avg('rating'))['avg'] or 0
        user_chapter.rating = round(avg_rating)
        user_chapter.save()

    # ---------------- Lesson type: quarter ----------------
    elif lesson.lesson_type == 'quarter':
        current_quarter = lesson.quarter
        quarter_user_lessons = UserLesson.objects.filter(
            user_subject=user_subject,
            lesson__quarter=current_quarter
        )
        q_lessons = quarter_user_lessons.filter(lesson__lesson_type='lesson')
        q_chapters = quarter_user_lessons.filter(lesson__lesson_type='chapter')

        user_sum_lesson = q_lessons.aggregate(s=Sum('rating'))['s'] or 0
        user_sum_chapter = q_chapters.aggregate(s=Sum('rating'))['s'] or 0

        lessons_in_quarter = Lesson.objects.filter(
            quarter=current_quarter, lesson_type='lesson'
        )
        chapters_in_quarter = Lesson.objects.filter(
            quarter=current_quarter, lesson_type='chapter'
        )

        max_sum_lesson = sum(
            l.tasks.aggregate(s=Sum('rating'))['s'] or 0 for l in lessons_in_quarter
        )
        max_sum_chapter = sum(
            l.tasks.aggregate(s=Sum('rating'))['s'] or 0 for l in chapters_in_quarter
        )

        # Бірінші бөлік (50%): (user_sum_lesson+user_sum_chapter)/(max_sum_lesson + max_sum_chapter) * 50
        max_value_chapter_and_lesson = max_sum_lesson + max_sum_chapter
        part1 = ((user_sum_lesson + user_sum_chapter) / max_value_chapter_and_lesson) * 50 if max_value_chapter_and_lesson else 0

        #Екінші бөлік(50 %): (quarter_rating / Lesson.rating) * 50
        quarter_rating = user_tasks.aggregate(total=Sum('rating'))['total'] or 0
        quarter_max = lesson.max_rating
        part2 = (quarter_rating / quarter_max) * 50 if quarter_max else 0

        user_lesson.percentage = round(part1 + part2, 2)
        user_lesson.rating = quarter_rating

    user_lesson.is_completed = True
    user_lesson.completed_at = timezone.now()
    user_lesson.status = 'finished'
    user_lesson.save()

    # ---------------- user_chapter percentages ----------------
    chapter_lessons = Lesson.objects.filter(chapter=lesson.chapter)
    user_chapter_lessons = UserLesson.objects.filter(user_subject=user_subject, lesson__in=chapter_lessons)
    chapter_total = user_chapter_lessons.count()
    chapter_completed = user_chapter_lessons.filter(is_completed=True).count()

    user_chapter.percentage = round((chapter_completed / chapter_total) * 100, 2) if chapter_total else 0
    user_chapter.is_completed = chapter_total > 0 and chapter_total == chapter_completed
    user_chapter.save()

    # ---------------- user_subject percentages ----------------
    subject_lessons = UserLesson.objects.filter(user_subject=user_subject)
    subject_total = subject_lessons.count()
    subject_completed = subject_lessons.filter(is_completed=True).count()

    user_subject.percentage = round((subject_completed / subject_total) * 100, 2) if subject_total else 0
    user_subject.is_completed = subject_total > 0 and subject_total == subject_completed
    if user_subject.is_completed:
        user_subject.completed_at = timezone.now()

    completed_quarters = subject_lessons.filter(
        lesson__lesson_type='quarter',
        is_completed=True
    )
    avg_quarter_percentage = completed_quarters.aggregate(avg=Avg('percentage'))['avg'] or 0
    if avg_quarter_percentage < 40:
        user_subject.rating = 2
    elif avg_quarter_percentage < 65:
        user_subject.rating = 3
    elif avg_quarter_percentage < 85:
        user_subject.rating = 4
    else:
        user_subject.rating = 5

    user_subject.save()

    messages.success(request, 'Сабақ сәтті аяқталды!')
    return redirect('user_lesson', subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id)


# Feedback handler
# ----------------------------------------------------------------------------------------------------------------------
@require_POST
@login_required
def feedback_handler(request, subject_id, chapter_id, lesson_id):
    user_lesson = get_object_or_404(UserLesson, id=lesson_id, user=request.user)

    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '')

    if not rating:
        return redirect('user_lesson', subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id)

    feedback, created = Feedback.objects.get_or_create(
        user_lesson=user_lesson,
        defaults={
            'rating': rating,
            'comment': comment,
        }
    )

    if not created:
        feedback.rating = rating
        feedback.comment = comment
        feedback.save()

    return redirect('user_lesson', subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id)


# user_lesson_task page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
@role_required('student')
def user_lesson_task_view(request, subject_id, chapter_id, lesson_id, task_id):
    user = request.user
    user_subject = get_object_or_404(UserSubject, user=user, pk=subject_id)
    user_chapter = get_object_or_404(UserChapter, user_subject=user_subject, pk=chapter_id)
    user_lesson = get_object_or_404(UserLesson, user_subject=user_subject, pk=lesson_id)
    user_task = get_object_or_404(UserTask.objects.select_related('task'), pk=task_id)
    user_tasks = user_lesson.user_tasks.order_by('task__order')

    # prev / next
    task_list = list(user_tasks)
    current_index = task_list.index(user_task) if user_task in task_list else -1
    prev_user_task = task_list[current_index - 1] if current_index > 0 else None
    next_user_task = task_list[current_index + 1] if 0 <= current_index < len(task_list) - 1 else None

    # POST
    if request.method == 'POST':
        handle_post_request(request, user_task)
        return redirect(
            'user_lesson_task',
            subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id, task_id=task_id
        )

    context = {
        'user_subject': user_subject,
        'user_chapter': user_chapter,
        'user_lesson': user_lesson,
        'user_task': user_task,
        'user_tasks': user_tasks,
        'task_type': user_task.task.task_type,
        'all_tasks_completed': not user_tasks.exclude(is_completed=True).exists(),
        'next_user_task': next_user_task,
        'prev_user_task': prev_user_task,
        **get_related_data(user_task),
    }
    return render(request, 'app/dashboard/student/user/subject/chapter/lesson/task/page.html', context)
