from django.contrib import admin
from core.models import UserSubject, UserLesson, UserChapter, UserTask


# UserSubject admin
# ----------------------------------------------------------------------------------------------------------------------
# UserChapter Tab
class UserChapterTab(admin.TabularInline):
    model = UserChapter
    extra = 0


# UserLesson Tab
class UserLessonTab(admin.TabularInline):
    model = UserLesson
    extra = 0


# UserSubject admin
@admin.register(UserSubject)
class UserSubjectAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'created_at', 'is_completed', 'subject_score', )
    list_filter = ('user', 'subject', 'is_completed', )
    search_fields = ('user__username', 'subject__title')
    inlines = (UserChapterTab, UserLessonTab, )


# UserLesson admin
# ----------------------------------------------------------------------------------------------------------------------
class UserTaskTab(admin.TabularInline):
    model = UserTask
    extra = 0


@admin.register(UserLesson)
class UserLessonAdmin(admin.ModelAdmin):
    list_display = ('user_subject', 'lesson', 'lesson_score', 'is_completed', 'completed_at', )
    list_filter = ('user_subject', 'lesson', 'is_completed', )
    search_fields = ('user__username', 'lesson__title')
    inlines = (UserTaskTab, )
