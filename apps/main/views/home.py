from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from core.models import Subject, UserSubject


# Home page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def home_view(request):
    user = request.user
    user_subjects = UserSubject.objects.filter(user=user)

    context = {
        'user_subjects': user_subjects
    }
    return render(request, 'app/page.html', context)



# Subjects page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def subjects_view(request):
    user = request.user
    subjects = Subject.objects.all()
    user_subjects_qs = UserSubject.objects.filter(user=user)
    user_subjects = {us.subject_id: us for us in user_subjects_qs}

    subject_list = []
    for subject in subjects:
        subject_list.append({
            'subject': subject,
            'user_subject': user_subjects.get(subject.id)
        })

    context = {
        'subject_list': subject_list
    }
    return render(request, 'app/subjects/page.html', context)



# Subject detail page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def subject_detail_view(request, pk):
    user = request.user
    subject = get_object_or_404(Subject, pk=pk)
    user_subject = UserSubject.objects.filter(user=user, subject=subject).first()

    context = {
        'subject': subject,
        'user_subject': user_subject
    }
    return render(request, 'app/subjects/detail/page.html', context)


# enroll subject handler
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def enroll_subject_handler(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    user = request.user

    user_subject, created = UserSubject.objects.get_or_create(
        user=user,
        subject=subject
    )

    if created:
        messages.success(request, f'Сіз «{subject.title}» пәніне жазылдыңыз.')
    else:
        messages.info(request, f'Сіз «{subject.title}» пәніне бұрын жазылғансыз.')

    return redirect('home')
