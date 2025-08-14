from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.models import UserSubject, UserChapter, UserLesson, UserTask, UserVideo, UserWritten, UserTextGap, \
    UserAnswer, UserMatching, Option
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


# User lesson task page
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

    # POST requests...
    if request.method == 'POST':
        if task_type == 'video':
            videos = user_task.user_videos.all()
            for uv in videos:
                watched_seconds = request.POST.get(f'watched_{uv.id}')
                print('watched_seconds:', watched_seconds)
                uv.watched_seconds = int(request.POST.get(f'watched_{uv.id}', 0))
                uv.is_completed = True
                uv.save()

            if all(uv.is_completed for uv in videos):
                user_task.is_completed = True
                user_task.score = user_task.task.task_score
                user_task.save()
                messages.success(request, 'Видеосабақ аяқталды!')

            return redirect(
                'user_lesson_task',
                subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id, task_id=task_id
            )

        elif task_type == 'written':
            for uw in user_task.user_written.all():
                answer = request.POST.get(f'answer_{uw.id}', '').strip()
                if answer:
                    uw.answer = answer
                    uw.is_submitted = True
                    uw.save()

            messages.success(request, 'Барлық жауаптар сәтті жіберілді!')
            return redirect(
                'user_lesson_task',
                subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id, task_id=task_id
            )

        elif task_type == 'text_gap':
            is_all_correct = True
            for user_text_gap in user_task.user_text_gaps.all():
                user_answer = request.POST.get(f'answer_{user_text_gap.id}', '').strip()
                correct_answer = user_text_gap.text_gap.correct_answer.strip()

                user_text_gap.answer = user_answer
                user_text_gap.is_correct = user_answer.lower() == correct_answer.lower()
                user_text_gap.save()

                if not user_text_gap.is_correct:
                    is_all_correct = False

            if is_all_correct:
                user_task.is_completed = True
                user_task.score = user_task.task.task_score
                user_task.save()
                messages.success(request, 'Барлық жауап дұрыс!')
            else:
                messages.error(request, 'Кейбір жауаптар дұрыс емес. Қайта тапсырып көріңіз!')

        elif task_type == 'test':
            total_score = 0

            for user_answer in user_task.user_options.select_related('question').prefetch_related('options'):
                selected_option_ids = request.POST.getlist(f'question_{user_answer.question.id}')
                selected_options = Option.objects.filter(id__in=selected_option_ids)

                user_answer.options.set(selected_options)
                correct_options = user_answer.question.options.filter(is_correct=True)

                if set(selected_options) == set(correct_options):
                    total_score += sum(opt.score for opt in correct_options)

            user_task.score = total_score
            user_task.is_completed = True
            user_task.save()

            messages.success(request, f'Сіз {total_score} балл жинадыңыз!')

            return redirect(
                'user_lesson_task',
                subject_id=subject_id, chapter_id=chapter_id, lesson_id=lesson_id, task_id=task_id
            )

        elif task_type == 'matching':
            correct = 0

            for um in user_task.matching_answers.select_related('pair'):
                selected = request.POST.get(f'selected_right_{um.id}', '').strip()
                um.selected_right = selected
                um.is_correct = selected == um.pair.right_item
                um.save()

                if um.is_correct:
                    correct += 1

            user_task.score = correct
            user_task.is_completed = True
            user_task.save()

            messages.success(request, f'Сәйкестендіру тапсырмасы аяқталды. Дұрыс жауаптар: {correct}')
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
        **related_data
    }

    return render(request, 'app/dashboard/student/user/subject/chapter/lesson/task/page.html', context)
