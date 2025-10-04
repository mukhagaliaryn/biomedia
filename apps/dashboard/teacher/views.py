from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.aggregates import Avg, Sum
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
    selected_class = request.GET.get('class')
    try:
        selected_quarter = int(request.GET.get('quarter', 1))
    except ValueError:
        selected_quarter = 1

    # -------------------- UserSubject (сынып фильтрімен) --------------------
    user_subjects = (
        UserSubject.objects
        .filter(subject=subject)
        .select_related('user', 'subject')
        .prefetch_related('user_chapters', 'user_lessons')
    )
    if selected_class:
        user_subjects = user_subjects.filter(user__user_class=selected_class)

    # -------------------- Орташа статистика --------------------
    user_subject_stats = user_subjects.aggregate(
        avg_percentage=Avg('percentage'),
        avg_rating=Avg('rating')
    )
    user_chapter_stats = UserChapter.objects.filter(user_subject__in=user_subjects).aggregate(
        avg_percentage=Avg('percentage'),
        avg_rating=Avg('rating')
    )
    user_lesson_stats = UserLesson.objects.filter(user_subject__in=user_subjects).aggregate(
        avg_percentage=Avg('percentage'),
        avg_rating=Avg('rating')
    )

    def safe_round(v): return round(v, 2) if v is not None else 0

    # -------------------- Қол жетімді сыныптар --------------------
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

    # -------------------- Бөлімдер мен сабақтар санау --------------------
    total_students = user_subjects.count()
    total_chapters = Chapter.objects.filter(subject=subject).count()
    total_lessons = Lesson.objects.filter(subject=subject).count()

    completed_chapters = 0
    for chapter in Chapter.objects.filter(subject=subject):
        done = UserChapter.objects.filter(
            user_subject__in=user_subjects, chapter=chapter, is_completed=True
        ).count()
        if total_students > 0 and done == total_students:
            completed_chapters += 1

    completed_lessons = 0
    for lesson in Lesson.objects.filter(subject=subject):
        done = UserLesson.objects.filter(
            user_subject__in=user_subjects, lesson=lesson, is_completed=True
        ).count()
        if total_students > 0 and done == total_students:
            completed_lessons += 1

    # -------------------- Тоқсандық БЖБ/ТЖБ есеп кестесі --------------------
    lessons = Lesson.objects.filter(
        subject=subject,
        lesson_type__in=['chapter', 'quarter'],
        quarter=selected_quarter
    ).order_by('lesson_type', 'order')

    report_data = []
    for lesson in lessons:
        # 🔹 Сынып фильтрі UserLesson арқылы да қолданылады
        ul_qs = UserLesson.objects.filter(
            user_subject__in=user_subjects,
            lesson=lesson
        )

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

    # -------------------- Жеке оқушылардың көрсеткіштері --------------------
    students_data = []
    for us in user_subjects:
        user_chapters = us.user_chapters.all()
        user_lessons = us.user_lessons.all()

        avg_chapter_percentage = user_chapters.aggregate(avg=Avg('percentage'))['avg'] or 0
        avg_chapter_rating = user_chapters.aggregate(avg=Avg('rating'))['avg'] or 0
        avg_lesson_percentage = user_lessons.aggregate(avg=Avg('percentage'))['avg'] or 0
        avg_lesson_rating = user_lessons.aggregate(avg=Avg('rating'))['avg'] or 0

        quarter_lessons = user_lessons.filter(lesson__lesson_type='quarter')
        avg_quarter_percentage = quarter_lessons.aggregate(avg=Avg('percentage'))['avg'] or 0

        students_data.append({
            'student': us.user,
            'user_class': us.user.user_class,
            'user_subject': us,
            'quarter_avg_percentage': round(avg_quarter_percentage, 2),
            'chapter_avg_percentage': round(avg_chapter_percentage, 2),
            'chapter_avg_rating': round(avg_chapter_rating, 2),
            'lesson_avg_percentage': round(avg_lesson_percentage, 2),
            'lesson_avg_rating': round(avg_lesson_rating, 2),
        })

    # -------------------- Контекст --------------------
    context = {
        'subject': subject,
        'user_subjects': user_subjects,
        'available_classes': available_classes,
        'selected_class': selected_class,
        'selected_quarter': selected_quarter,
        'quarters': [1, 2, 3, 4],
        'report_data': report_data,
        'students_data': students_data,
        'statistics': {
            'user_subject_avg_percentage': safe_round(user_subject_stats['avg_percentage']),
            'user_subject_avg_rating': safe_round(user_subject_stats['avg_rating']),
            'user_chapter_avg_percentage': safe_round(user_chapter_stats['avg_percentage']),
            'user_chapter_avg_rating': safe_round(user_chapter_stats['avg_rating']),
            'user_lesson_avg_percentage': safe_round(user_lesson_stats['avg_percentage']),
            'user_lesson_avg_rating': safe_round(user_lesson_stats['avg_rating']),
            'total_chapters': total_chapters,
            'completed_chapters': completed_chapters,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
        },
    }

    return render(request, 'app/dashboard/teacher/subject/page.html', context)
