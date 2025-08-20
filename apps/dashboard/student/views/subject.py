from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from core.models import UserSubject, UserChapter, UserLesson, UserTask, UserVideo, UserWritten, UserTextGap, \
    UserAnswer, Option, Task
from core.utils.decorators import role_required


# user_lesson page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
@role_required('student')
def user_lesson_view(request, subject_id, chapter_id, lesson_id):
    user = request.user
    user_subject = get_object_or_404(UserSubject, user=user, pk=subject_id)
    user_chapter = get_object_or_404(UserChapter, user_subject=user_subject, pk=chapter_id)
    user_lesson = get_object_or_404(UserLesson, user_subject=user_subject, pk=lesson_id)
    tasks = user_lesson.lesson.tasks.exclude(task_type='video')
    user_lessons_qs = UserLesson.objects.filter(user_subject=user_subject).order_by('lesson__order')

    # ------------------ link for user tasks ------------------
    first_task = (
        UserTask.objects
        .filter(user_lesson=user_lesson)
        .select_related('task')
        .order_by('task__order')
        .first()
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
    }

    return render(request, 'app/dashboard/student/user/subject/chapter/lesson/page.html', context)


# actions
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

    user_lesson.status = 'in-progress'
    user_lesson.started_at = timezone.now()
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


# user_lesson_task page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
@role_required('student')
def user_lesson_task_view(request, subject_id, chapter_id, lesson_id, task_id):
    user = request.user
    user_subject = get_object_or_404(UserSubject, user=user, pk=subject_id)
    user_chapter = get_object_or_404(UserChapter, user_subject=user_subject, pk=chapter_id)
    user_lesson = get_object_or_404(UserLesson, user_subject=user_subject, pk=lesson_id)
    user_task = get_object_or_404(UserTask, pk=task_id)
    user_tasks = UserTask.objects.filter(user_lesson=user_lesson).order_by('task__order')

    # ---------------------- prev, next links ----------------------
    next_user_task = None
    prev_user_task = None

    task_list = list(user_tasks)
    try:
        current_index = task_list.index(user_task)
        if current_index > 0:
            prev_user_task = task_list[current_index - 1]
        if current_index < len(task_list) - 1:
            next_user_task = task_list[current_index + 1]
    except ValueError:
        pass

    related_data = {}

    task_type = user_task.task.task_type

    if task_type == 'video':
        related_data['user_videos'] = user_task.user_videos.all()

    elif task_type == 'written':
        related_data['user_written'] = user_task.user_written.all()

    elif task_type == 'text_gap':
        related_data['user_text_gaps'] = user_task.user_text_gaps.all()

    elif task_type == 'test':
        related_data['user_answers'] = user_task.user_options.select_related('question').prefetch_related('options')

    elif task_type == 'matching':
        related_data['user_matchings'] = user_task.matching_answers.all()

    all_tasks_completed = not user_tasks.exclude(is_completed=True).exists()

    # POST requests...
    if request.method == 'POST':
        # -------------- video --------------
        if task_type == 'video':
            videos = user_task.user_videos.all()
            for uv in videos:
                uv.watched_seconds = int(request.POST.get(f'watched_{uv.id}', 0))
                uv.is_completed = True
                uv.save()

            if all(uv.is_completed for uv in videos):
                user_task.is_completed = True
                user_task.rating = user_task.task.rating
                user_task.save()
                messages.success(request, 'Видеосабақ аяқталды!')

            return redirect(
                'user_lesson_task',
                subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id, task_id=task_id
            )

        # -------------- written --------------
        elif task_type == 'written':
            for uw in user_task.user_written.all():
                answer = request.POST.get(f'answer_{uw.id}', '').strip()
                uploaded_file = request.FILES.get(f'file_{uw.id}')
                if answer or uploaded_file:
                    if answer:
                        uw.answer = answer
                    if uploaded_file:
                        uw.file = uploaded_file
                    uw.is_submitted = True
                    uw.save()

            messages.success(request, 'Барлық жауаптар сәтті жіберілді!')
            return redirect(
                'user_lesson_task',
                subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id, task_id=task_id
            )

        # -------------- text_gap --------------
        elif task_type == 'text_gap':
            total = user_task.user_text_gaps.count()
            correct = 0

            for user_text_gap in user_task.user_text_gaps.all():
                user_answer = request.POST.get(f'answer_{user_text_gap.id}', '').strip()
                correct_answer = user_text_gap.text_gap.correct_answer.strip()

                is_correct = user_answer.lower() == correct_answer.lower()

                user_text_gap.answer = user_answer
                user_text_gap.is_correct = is_correct
                user_text_gap.save()

                if is_correct:
                    correct += 1

            incorrect = total - correct
            full_rating = user_task.task.rating

            if correct == total:
                user_task.rating = full_rating
                messages.success(request, 'Барлық жауап дұрыс!')
            elif incorrect == 1:
                if full_rating == 1:
                    user_task.rating = 0
                    messages.warning(request,
                                     'Бір қате жібердіңіз. Бұл тапсырма тек 1 баллдық болғандықтан, ұпай берілмейді.')
                else:
                    user_task.rating = int(full_rating / 2)
                    messages.info(request, 'Бір қате бар. Жарты ұпай алдыңыз.')
            elif incorrect >= (total / 2):
                user_task.rating = 0
                messages.error(request, 'Қателер жартысынан көп. Ұпай берілмейді.')
            else:
                if full_rating == 1:
                    user_task.rating = 0
                    messages.warning(request,
                                     'Кем дегенде бір дұрыс бар, бірақ тапсырма 1 баллдық болғандықтан ұпай берілмейді.')
                else:
                    user_task.rating = int(full_rating / 2)
                    messages.warning(request, 'Бірнеше қате бар. Жарты ұпай алдыңыз.')

            user_task.is_completed = True
            user_task.save()
            return redirect(
                'user_lesson_task',
                subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id, task_id=task_id
            )

        # -------------- test --------------
        elif task_type == 'test':
            total_score = 0
            any_answered = False

            for user_answer in user_task.user_options.select_related('question').prefetch_related('question__options'):
                question = user_answer.question
                selected_option_ids = request.POST.getlist(f'question_{question.id}')

                if selected_option_ids:
                    any_answered = True

                valid_option_ids = set(question.options.values_list('id', flat=True))
                selected_option_ids = [int(opt_id) for opt_id in selected_option_ids if int(opt_id) in valid_option_ids]

                selected_options = Option.objects.filter(id__in=selected_option_ids)
                user_answer.options.set(selected_options)

                correct_option_ids = set(
                    question.options.filter(is_correct=True).values_list('id', flat=True)
                )

                if set(selected_option_ids) == correct_option_ids:
                    total_score += sum(
                        question.options.filter(id__in=correct_option_ids).values_list('score', flat=True)
                    )

            if any_answered:
                user_task.rating = total_score
                user_task.is_completed = True
                user_task.save()
                messages.success(request, f'Сіз {total_score} балл жинадыңыз!')
            else:
                messages.error(request, 'Сіз ешбір сұраққа жауап бермедіңіз')

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
        'task_type': task_type,
        'all_tasks_completed': all_tasks_completed,
        'next_user_task': next_user_task,
        'prev_user_task': prev_user_task,
        **related_data
    }

    return render(request, 'app/dashboard/student/user/subject/chapter/lesson/task/page.html', context)



@login_required
@role_required('student')
@require_POST
def lesson_finish_handler(request, subject_id, chapter_id, lesson_id):
    user = request.user

    user_subject = get_object_or_404(UserSubject, user=user, pk=subject_id)
    user_chapter = get_object_or_404(UserChapter, user_subject=user_subject, pk=chapter_id)
    user_lesson = get_object_or_404(UserLesson, user_subject=user_subject, pk=lesson_id)

    user_tasks = UserTask.objects.filter(user_lesson=user_lesson)

    # 1. user_lesson
    if not user_lesson.is_completed:
        total_rating = user_tasks.aggregate(total=Sum('rating')).get('total', 0)
        user_lesson.rating = total_rating
        user_lesson.status = 'finished'
        user_lesson.completed_at = timezone.now()
        user_lesson.is_completed = True

        total_user_lessons = UserLesson.objects.filter(user_subject=user_subject).count()
        completed_user_lessons = UserLesson.objects.filter(user_subject=user_subject, is_completed=True).count()
        user_lesson.percentage = round((completed_user_lessons / total_user_lessons) * 100, 2) if total_user_lessons else 0
        user_lesson.save()
        messages.success(request, 'Сабақ сәтті аяқталды!')

    # 2. user_chapter
    chapter_lessons = UserLesson.objects.filter(user_subject=user_subject, lesson__chapter=user_chapter.chapter)
    total_chapter_rating = chapter_lessons.aggregate(total=Sum('rating')).get('total', 0)
    chapter_total_count = UserChapter.objects.filter(user_subject=user_subject).count()
    chapter_completed_count = UserChapter.objects.filter(user_subject=user_subject, is_completed=True).count()


    user_chapter.rating = total_chapter_rating
    user_chapter.percentage = round((chapter_completed_count / chapter_total_count) * 100, 2) if chapter_total_count else 0
    user_chapter.is_completed = chapter_completed_count == chapter_total_count
    user_chapter.save()

    # 3. user_subject
    subject_lessons = UserLesson.objects.filter(user_subject=user_subject)
    subject_rating_total = subject_lessons.aggregate(total=Sum('rating')).get('total', 0)
    subject_completed = subject_lessons.filter(is_completed=True).count()
    subject_total = subject_lessons.count()

    user_subject.rating = subject_rating_total
    user_subject.percentage = round((subject_completed / subject_total) * 100, 2) if subject_total else 0
    user_subject.is_completed = subject_completed == subject_total
    if user_subject.is_completed:
        user_subject.completed_at = timezone.now()
    user_subject.save()

    return redirect(
        'user_lesson',
        subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id,
    )
