from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from core.utils.decorators import role_required


@login_required
@role_required('teacher')
def teacher_view(request):
    return HttpResponse('Teacher page')