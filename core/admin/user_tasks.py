from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from core.models import UserTask, UserVideo, UserWritten, UserTextGap, UserAnswer, UserMatchingAnswer


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


class UserMatchingAnswerTab(admin.TabularInline):
    model = UserMatchingAnswer
    extra = 0


@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = ('user_lesson', 'task', 'submitted_at', 'rating', 'is_completed', )
    list_filter = ('user_lesson', 'task', 'is_completed', )
    inlines = (UserVideoTab, UserWrittenTab, UserTextGapTab, UserAnswerTab, UserMatchingAnswerTab, )
    readonly_fields = ('user_lesson_link',)

    def user_lesson_link(self, obj):
        if obj.user_lesson:
            url = reverse('admin:core_userlesson_change', args=[obj.user_lesson.id])
            return format_html('<a href="{}" class="view-link">🔗 {}</a>', url, obj.user_lesson)
        return '-'

    user_lesson_link.short_description = 'Қолданушының сабағы'