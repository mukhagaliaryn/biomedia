from django.contrib import admin
from core.models import UserTask, UserVideo, UserWritten, UserTextGap, UserAnswer, UserMatching


# UserTask admin
# ----------------------------------------------------------------------------------------------------------------------
class UserVideoTab(admin.TabularInline):
    model = UserVideo
    extra = 0


class UserWrittenTab(admin.TabularInline):
    model = UserWritten
    extra = 0


class UserTextGapTab(admin.TabularInline):
    model = UserTextGap
    extra = 0


class UserAnswerTab(admin.TabularInline):
    model = UserAnswer
    extra = 0


class UserMatchingTab(admin.TabularInline):
    model = UserMatching
    extra = 0


@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = ('user_lesson', 'task', 'submitted_at', 'score', 'is_completed', )
    list_filter = ('user_lesson', 'task', 'is_completed', )
    inlines = (UserVideoTab, UserWrittenTab, UserTextGapTab, UserAnswerTab, UserMatchingTab, )