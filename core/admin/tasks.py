from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django_summernote.admin import SummernoteModelAdmin, SummernoteModelAdminMixin
from core.models import Task, Question, Option, Written, Pair, TextGap, Video


# Task admin
# ----------------------------------------------------------------------------------------------------------------------
# Video Tab
class VideoTab(admin.TabularInline):
    model = Video
    extra = 0


# Written Tab
class WrittenTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Written
    extra = 0


# TextGap Tab
class TextGapTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = TextGap
    extra = 0


# Question Tab
class QuestionTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Question
    fields = ('order', 'text', 'question_type', 'view_link', )
    extra = 0
    readonly_fields = ('view_link', )

    def view_link(self, obj):
        if obj.pk:
            url = reverse('admin:core_question_change', args=[obj.pk])
            return format_html('<a href="{}" class="view-link">Толығырақ</a>', url)
        return '-'

    view_link.short_description = 'Сұраққа сілтеме'


# MatchingPair Tab
class MatchingPairTab(admin.TabularInline):
    model = Pair
    fields = ('left_item', 'right_item', )
    extra = 0


# Task admin
@admin.register(Task)
class TaskAdmin(SummernoteModelAdmin):
    list_display = ('lesson', 'task_score', 'order', )
    readonly_fields = ('lesson_link', )
    inlines = (VideoTab, WrittenTab, TextGapTab, QuestionTab, MatchingPairTab, )

    def lesson_link(self, obj):
        if obj.lesson:
            url = reverse('admin:core_lesson_change', args=[obj.lesson.id])
            return format_html('<a href="{}" class="view-link">🔗 {} пәніне өту</a>', url, obj.lesson.title)
        return '-'

    lesson_link.short_description = 'Сабаққа сілтеме'


# Task type:Test admin
# ----------------------------------------------------------------------------------------------------------------------
# Option
class OptionTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Option
    extra = 0


@admin.register(Question)
class QuestionAdmin(SummernoteModelAdmin):
    readonly_fields = ('task_link', )
    inlines = (OptionTab, )

    def task_link(self, obj):
        if obj.task:
            url = reverse('admin:core_task_change', args=[obj.task.id])
            return format_html('<a href="{}" class="view-link">🔗 {} тапсырмаға өту</a>', url, obj.task)
        return '— сұрақпен байланыспаған'

    task_link.short_description = 'Сұраққа сілтеме'


# Task type:TextGap admin
# ----------------------------------------------------------------------------------------------------------------------
@admin.register(TextGap)
class TextGapAdmin(SummernoteModelAdmin):
    readonly_fields = ('task_link',)

    def task_link(self, obj):
        if obj.task:
            url = reverse('admin:core_task_change', args=[obj.task.id])
            return format_html('<a href="{}" class="view-link">🔗 {} тапсырмасына өту</a>', url, obj.task.get_task_type_display())
        return '— тапсырмамен байланыспаған'

    task_link.short_description = 'Тапсырмаға сілтеме'
