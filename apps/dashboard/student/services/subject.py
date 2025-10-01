from django.contrib import messages
from core.models import Option, TableCell


def get_related_data(user_task):
    task_type = user_task.task.task_type
    BUILDERS = {
        'video': lambda ut: {'user_videos': ut.user_videos.all()},
        'written': lambda ut: {'user_written': ut.user_written.all()},
        'text_gap': lambda ut: {'user_text_gaps': ut.user_text_gaps.all()},
        'test': lambda ut: {'user_answers': ut.user_options.all()},
        'matching': lambda ut: {'user_matchings': ut.matching_answers.all()},
        'table': build_table_context,
    }
    builder = BUILDERS.get(task_type, lambda ut: {})
    return builder(user_task)


def build_table_context(user_task):
    rows = user_task.task.table_rows.order_by('order')
    columns = user_task.task.table_columns.order_by('order')
    answers = user_task.user_table_answers.select_related('row', 'column')

    answer_matrix = {row.id: {} for row in rows}
    for a in answers:
        answer_matrix[a.row_id][a.column_id] = a

    correct_cells = TableCell.objects.filter(row__task=user_task.task)
    correct_matrix = {row.id: {} for row in rows}
    for cell in correct_cells:
        correct_matrix[cell.row_id][cell.column_id] = cell.correct

    return {
        'table_rows': rows,
        'table_columns': columns,
        'answer_matrix': answer_matrix,
        'correct_matrix': correct_matrix,
    }


def handle_post_request(request, user_task):
    task_type = user_task.task.task_type
    HANDLERS = {
        'video': handle_video,
        'written': handle_written,
        'text_gap': handle_text_gap,
        'test': handle_test,
        'matching': handle_matching,
        'table': handle_table,
    }
    handler = HANDLERS.get(task_type)
    if handler:
        handler(request, user_task)


# ---------------- video ----------------
def handle_video(request, user_task):
    videos = user_task.user_videos.all()
    for uv in videos:
        uv.watched_seconds = int(request.POST.get(f'watched_{uv.id}', 0))
        uv.is_completed = True
        uv.save()
    if all(uv.is_completed for uv in videos):
        user_task.is_completed = True
        user_task.rating = user_task.task.rating
        user_task.save()
        messages.success(request, 'Видеосабақ аяқталды')


# ---------------- written ----------------
def handle_written(request, user_task):
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
    messages.success(request, 'Жауаптар жіберілді')


# ---------------- text_gap ----------------
def handle_text_gap(request, user_task):
    total = user_task.user_text_gaps.count()
    correct = 0
    for utg in user_task.user_text_gaps.all():
        user_answer = request.POST.get(f'answer_{utg.id}', '').strip()
        is_correct = user_answer.lower() == utg.text_gap.correct_answer.strip().lower()
        utg.answer = user_answer
        utg.is_correct = is_correct
        utg.save()
        if is_correct:
            correct += 1

    incorrect = total - correct
    full_rating = user_task.task.rating

    if correct == total:
        score = full_rating
        messages.success(request, 'Барлық жауап дұрыс')
    elif incorrect == 1:
        score = full_rating / 2 if full_rating > 1 else 0
        messages.warning(request, 'Бір қате бар. Жарты ұпай')
    elif incorrect >= total / 2:
        score = 0
        messages.error(request, 'Қателер көп. Ұпай берілмейді')
    else:
        score = full_rating / 2 if full_rating > 1 else 0
        messages.info(request, 'Бірнеше қате бар. Жарты ұпай')

    user_task.rating = score
    user_task.is_completed = True
    user_task.save()


# ---------------- test ----------------
def handle_test(request, user_task):
    total = user_task.user_options.count()
    correct = 0
    has_incorrect_simple = False
    multiple_incorrects = 0

    for ua in user_task.user_options.select_related('question'):
        q = ua.question
        selected_ids = list(map(int, request.POST.getlist(f'question_{q.id}')))
        valid_ids = set(q.options.values_list('id', flat=True))
        selected_ids = [opt_id for opt_id in selected_ids if opt_id in valid_ids]
        ua.options.set(Option.objects.filter(id__in=selected_ids))

        correct_ids = set(q.options.filter(is_correct=True).values_list('id', flat=True))
        if q.question_type == 'simple':
            if set(selected_ids) == correct_ids:
                correct += 1
            else:
                has_incorrect_simple = True
        elif q.question_type == 'multiple':
            if set(selected_ids) == correct_ids:
                correct += 1
            else:
                multiple_incorrects += 1

    full_rating = user_task.task.rating
    if has_incorrect_simple:
        score = 0
    elif multiple_incorrects == 1:
        score = full_rating / 2 if full_rating > 1 else 0
    elif multiple_incorrects > 1:
        score = 0
    elif correct == total:
        score = full_rating
    else:
        score = full_rating / 2 if full_rating > 1 else 0

    user_task.rating = score
    user_task.is_completed = True
    user_task.save()


# ---------------- matching ----------------
def handle_matching(request, user_task):
    for answer in user_task.matching_answers.all():
        selected_column_id = request.POST.get(f'column_{answer.item.id}')
        if selected_column_id:
            answer.selected_column_id = int(selected_column_id)
            answer.check_answer()

    total = user_task.matching_answers.count()
    correct = user_task.matching_answers.filter(is_correct=True).count()
    wrong = total - correct
    full_rating = user_task.task.rating

    if wrong == 0:
        score = full_rating
    elif wrong == 1:
        score = full_rating / 2 if full_rating > 1 else 0
    elif wrong > total / 2:
        score = 0
    else:
        score = full_rating / 2 if full_rating > 1 else 0

    user_task.rating = score
    user_task.is_completed = True
    user_task.save()


# ---------------- table ----------------
def handle_table(request, user_task):
    correct_map = {
        (c.row_id, c.column_id): c.correct
        for c in TableCell.objects.filter(row__task=user_task.task)
    }

    total, correct = 0, 0
    for ans in user_task.user_table_answers.all():
        is_checked = request.POST.get(f'cell_{ans.row_id}_{ans.column_id}') == 'on'
        ans.checked = is_checked
        ans.is_submitted = True
        ans.save()
        if correct_map.get((ans.row_id, ans.column_id)) == is_checked:
            correct += 1
        total += 1

    rating = user_task.task.rating or 1
    if correct == total:
        score = rating
    elif correct >= total / 2:
        score = rating / 2
    else:
        score = 0

    user_task.rating = score
    user_task.is_completed = True
    user_task.save()