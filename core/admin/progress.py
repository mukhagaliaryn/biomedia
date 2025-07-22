from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from core.models import UserSubject, UserLesson, UserChapter


# UserSubject admin
# ----------------------------------------------------------------------------------------------------------------------
@admin.register(UserSubject)
class UserSubjectAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'created_at', 'is_completed', 'subject_score', )
    list_filter = ('user', 'subject', 'is_completed', )
    search_fields = ('user__username', 'subject__title')


# UserChapter admin
# ----------------------------------------------------------------------------------------------------------------------
@admin.register(UserChapter)
class UserChapterAdmin(admin.ModelAdmin):
    list_display = ('user_subject', 'chapter', 'chapter_score', 'is_completed', )
    list_filter = ('user_subject', 'chapter', 'is_completed', )
    search_fields = ('user__username', 'lesson__title')


# UserLesson admin
# ----------------------------------------------------------------------------------------------------------------------
@admin.register(UserLesson)
class UserLessonAdmin(admin.ModelAdmin):
    list_display = ('user_subject', 'lesson', 'lesson_score', 'is_completed', 'completed_at', )
    list_filter = ('user_subject', 'lesson', 'is_completed', )
    search_fields = ('user__username', 'lesson__title')
