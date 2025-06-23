from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def main_view(request):
    return render(request, 'app/page.html')
