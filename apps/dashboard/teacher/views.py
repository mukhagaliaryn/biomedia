from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.aggregates import Avg, Sum, Count
from django.shortcuts import render, get_object_or_404

from core.models import Subject, UserSubject, UserChapter, UserLesson, User, Lesson, Chapter
from core.utils.decorators import role_required


# Teacher dashboard page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
@role_required('teacher')
def teacher_view(request):
    subjects_data = []

    for subject in Subject.objects.all():
        user_subjects = UserSubject.objects.filter(subject=subject)
        subject_avg = user_subjects.aggregate(
            avg_rating=Avg('rating'),
            avg_percentage=Avg('percentage')
        )
        chapter_stats = UserChapter.objects.filter(user_subject__subject=subject).aggregate(
            avg_rating=Avg('rating'),
            avg_percentage=Avg('percentage')
        )
        lesson_stats = UserLesson.objects.filter(user_subject__subject=subject).aggregate(
            avg_rating=Avg('rating'),
            avg_percentage=Avg('percentage')
        )

        def safe_round(value):
            return round(value) if value is not None else 0

        subjects_data.append({
            'subject': subject,
            'students': user_subjects[:3],
            # user_subjects avg
            'subject_avg_rating': safe_round(subject_avg['avg_rating']),
            'subject_avg_percentage': safe_round(subject_avg['avg_percentage']),
            # user_chapters avg
            'chapter_avg_rating': safe_round(chapter_stats['avg_rating']),
            'chapter_avg_percentage': safe_round(chapter_stats['avg_percentage']),
            # user_lessons avg
            'lesson_avg_rating': safe_round(lesson_stats['avg_rating']),
            'lesson_avg_percentage': safe_round(lesson_stats['avg_percentage']),
        })

    context = {
        'generics': {
            'classes_count': 2,
            'subjects_count': Subject.objects.all().count(),
            'students_count': UserSubject.objects.all().count()
        },
        'subjects_data': subjects_data,
    }
    return render(request, 'app/dashboard/teacher/page.html', context)


# Subject manage page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
@role_required('teacher')
def subject_manage_view(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)

    # -------------------- Фильтр параметрлері --------------------
    selected_class = request.GET.get('class') or ''
    selected_quarter = request.GET.get('quarter') or '1'
    selected_quarter = str(selected_quarter)
    if selected_quarter not in {'1', '2', '3', '4'}:
        selected_quarter = '1'

    # UserSubject (сынып фильтрімен)
    user_subjects = (
        UserSubject.objects.filter(subject=subject)
        .select_related('user', 'subject')
        .order_by('user__first_name', 'user__last_name',)
    )
    if selected_class:
        user_subjects = user_subjects.filter(user__user_class=selected_class)

    total_students = user_subjects.count()

    # Қол жетімді сыныптар
    available_classes = [
        (c, dict(User.USER_CLASS).get(c, c))
        for c in (
            User.objects
            .filter(user_subjects__subject=subject)
            .values_list('user_class', flat=True)
            .distinct()
            .order_by('user_class')
        )
    ]

    # -------------------- Прогресс сандары --------------------
    # Барлық бөлімдер мен сабақтар
    chapters = Chapter.objects.filter(subject=subject)
    lessons = Lesson.objects.filter(subject=subject, lesson_type='lesson', quarter=selected_quarter)

    total_chapters = chapters.count()
    total_lessons = lessons.count()

    # Барлық оқушылар толық аяқтаған бөлімдер
    if total_students > 0:
        completed_chapters = (
            UserChapter.objects.filter(user_subject__in=user_subjects, chapter__in=chapters, is_completed=True)
            .values('chapter').annotate(cnt=Count('chapter')).filter(cnt=total_students).count()
        )
        # Барлық оқушылар толық аяқтаған сабақтар
        completed_lessons = (
            UserLesson.objects.filter(user_subject__in=user_subjects, lesson__in=lessons, is_completed=True)
            .values('lesson').annotate(cnt=Count('lesson')).filter(cnt=total_students).count()
        )
    else:
        completed_chapters = 0
        completed_lessons = 0

    # Орташа пайызбен баға
    user_subjects_avg = user_subjects.aggregate(avg_percentage=Avg('percentage'), avg_rating=Avg('rating'))

    def safe_round(v):
        return round(v, 2) if v is not None else 0


    # -------------------- Тоқсандық БЖБ/ТЖБ есеп кестесі --------------------
    lessons = Lesson.objects.filter(
        subject=subject,
        lesson_type__in=['chapter', 'quarter'],
        quarter=selected_quarter
    ).order_by('lesson_type', 'order')

    report_data = []
    for lesson in lessons:
        # Сынып фильтрі UserLesson арқылы да қолданылады
        ul_qs = UserLesson.objects.filter(user_subject__in=user_subjects, lesson=lesson)

        students_count = ul_qs.values('user_subject_id').distinct().count()
        max_score = getattr(lesson, 'max_rating', None)
        if max_score is None:
            max_score = lesson.tasks.aggregate(total=Sum('rating'))['total'] or 0

        low  = ul_qs.filter(percentage__lt=40).count()
        mid  = ul_qs.filter(percentage__gte=40, percentage__lt=85).count()
        high = ul_qs.filter(percentage__gte=85).count()

        report_data.append({
            'lesson': lesson,
            'lesson_type': lesson.get_lesson_type_display(),
            'students_count': students_count,
            'max_score': max_score,
            'low': low,
            'mid': mid,
            'high': high,
        })

    # -------------------- Оқушылардың тоқсандық бағалар кестесі --------------------
    chapter_lessons = (
        Lesson.objects.filter(subject=subject, lesson_type='chapter', quarter=selected_quarter).order_by('order')
    )
    quarter_lesson = Lesson.objects.filter(subject=subject, lesson_type='quarter', quarter=selected_quarter).first()

    # Оқушылар
    students_data = []
    for us in user_subjects:
        lessons_qs = UserLesson.objects.filter(
            user_subject=us,
            lesson__quarter=selected_quarter
        ).select_related('lesson')

        # Формативті (lesson типі)
        lesson_grades = list(lessons_qs.filter(lesson__lesson_type='lesson').values_list('rating', flat=True))
        lesson_score_sum = sum([g for g in lesson_grades if g is not None])
        lesson_count = len(lesson_grades)

        # БЖБ (chapter типі)
        chapter_grades = []
        chapter_score_sum = 0
        for ch in chapter_lessons:
            grade = lessons_qs.filter(lesson=ch).values_list('rating', flat=True).first()
            grade_val = grade if grade is not None else 0
            chapter_grades.append(grade if grade is not None else '-')
            chapter_score_sum += grade_val

        # ТЖБ (quarter типі)
        quarter_grade = None
        if quarter_lesson:
            quarter_grade = lessons_qs.filter(lesson=quarter_lesson).values_list('rating', flat=True).first()
            quarter_max = getattr(quarter_lesson, 'max_rating', 0) or 0
        else:
            quarter_max = 0

        # Макс. мәндер
        chapter_max_sum = sum([getattr(ch, 'max_rating', 0) or 0 for ch in chapter_lessons])
        lesson_max_sum = lesson_count * 10  # әр lesson 10 баллдық деп алынады

        # Есептеу формулалары
        fb_bjb_percent = 0
        if (chapter_max_sum + lesson_max_sum) > 0:
            fb_bjb_percent = ((chapter_score_sum + lesson_score_sum) / (chapter_max_sum + lesson_max_sum)) * 50

        tjb_percent = 0
        if quarter_grade and quarter_max:
            tjb_percent = (quarter_grade / quarter_max) * 50

        total_percent = fb_bjb_percent + tjb_percent
        if total_percent > 100:
            total_percent = 100

        # Тоқсандық баға (5 балдық шкала)
        if total_percent <= 40:
            quarter_mark = 2
        elif total_percent <= 65:
            quarter_mark = 3
        elif total_percent <= 85:
            quarter_mark = 4
        else:
            quarter_mark = 5

        # Қорытынды
        students_data.append({
            'student': us.user,
            'lesson_grades': lesson_grades,
            'chapter_grades': chapter_grades,
            'quarter_grade': quarter_grade or '-',
            'fb_bjb_percent': round(fb_bjb_percent, 2),
            'tjb_percent': round(tjb_percent, 2),
            'total_percent': round(total_percent, 2),
            'quarter_mark': quarter_mark,
        })

    # -------------------- Орташа мәндер (фильтрге сәйкес) --------------------
    if students_data:
        fb_bjb_avg = sum(s['fb_bjb_percent'] for s in students_data) / len(students_data)
        tjb_avg = sum(s['tjb_percent'] for s in students_data) / len(students_data)
        total_avg = sum(s['total_percent'] for s in students_data) / len(students_data)
        mark_avg = sum(s['quarter_mark'] for s in students_data) / len(students_data)
    else:
        fb_bjb_avg = tjb_avg = total_avg = mark_avg = 0

    fb_bjb_progress = round(fb_bjb_avg * 2, 2)
    tjb_progress = round(tjb_avg * 2, 2)
    total_progress = round(total_avg, 2)

    # -------------------- Контекст --------------------
    context = {
        'subject': subject,
        'available_classes': available_classes,
        'selected_class': selected_class,
        'selected_quarter': selected_quarter,
        'quarters': ['1', '2', '3', '4'],
        'generics': {
            'total_chapters': total_chapters,
            'completed_chapters': completed_chapters,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'user_subjects_avg_percentage': safe_round(user_subjects_avg['avg_percentage']),
            'user_subjects_avg_rating': safe_round(user_subjects_avg['avg_rating']),
        },
        'report_data': report_data,
        'chapter_lessons': chapter_lessons,
        'quarter_lesson': quarter_lesson,
        'students_data': students_data,
        'averages': {
            'fb_bjb_avg': round(fb_bjb_avg, 2),
            'tjb_avg': round(tjb_avg, 2),
            'total_avg': round(total_avg, 2),
            'mark_avg': round(mark_avg, 2),

            'fb_bjb_progress': fb_bjb_progress,
            'tjb_progress': tjb_progress,
            'total_progress': total_progress,
        }
    }

    return render(request, 'app/dashboard/teacher/subject/page.html', context)