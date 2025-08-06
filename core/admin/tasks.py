from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django_summernote.admin import SummernoteModelAdmin, SummernoteModelAdminMixin
from core.models import Task, Question, Option, Test, Written, Matching, Pair, TextGap


# Task admin
# ----------------------------------------------------------------------------------------------------------------------
# Written Tab
class WrittenTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Written
    extra = 0


# TextGap Tab
class TextGapTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = TextGap
    extra = 0


# Matching Tab
class MatchingTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Matching
    fields = ('task', 'instruction', 'view_link', )
    extra = 0
    readonly_fields = ('view_link',)

    # Detail view
    def view_link(self, obj):
        if obj.pk:
            url = reverse('admin:core_matching_change', args=[obj.pk])
            return format_html('<a href="{}" class="view-link">Толығырақ</a>', url)
        return '-'

    view_link.short_description = _('Сәйкестендіру сілтемесі')


# Test Tab
class TestTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Test
    fields = ('task', 'instruction', 'view_link', )
    extra = 0
    readonly_fields = ('view_link',)

    # Detail view
    def view_link(self, obj):
        if obj.pk:
            url = reverse('admin:core_test_change', args=[obj.pk])
            return format_html('<a href="{}" class="view-link">Толығырақ</a>', url)
        return '-'

    view_link.short_description = _('Тест сілтемесі')


# Task admin
@admin.register(Task)
class TaskAdmin(SummernoteModelAdmin):
    list_display = ('lesson', 'task_score', 'order', )
    readonly_fields = ('lesson_link', )
    inlines = (WrittenTab, TextGapTab, MatchingTab, TestTab, )

    def lesson_link(self, obj):
        if obj.lesson:
            url = reverse('admin:core_lesson_change', args=[obj.lesson.id])
            return format_html('<a href="{}" class="view-link">🔗 {} пәніне өту</a>', url, obj.lesson.title)
        return '— сабақ байланыспаған'

    lesson_link.short_description = 'Сабаққа сілтеме'


# Task type:Test admin
# ----------------------------------------------------------------------------------------------------------------------
# Question
class QuestionTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Question
    fields = ('text', 'question_type', 'order', 'view_link', )
    extra = 0
    readonly_fields = ('view_link',)

    def view_link(self, obj):
        if obj.pk:
            url = reverse('admin:core_question_change', args=[obj.pk])
            return format_html('<a href="{}" class="view-link">Толығырақ</a>', url)
        return '-'

    view_link.short_description = _('Сұрақ сілтемесі')


# Option
class OptionTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Option
    extra = 0


@admin.register(Test)
class TestAdmin(SummernoteModelAdmin):
    readonly_fields = ('task_link', )
    inlines = (QuestionTab, )

    def task_link(self, obj):
        if obj.task:
            url = reverse('admin:core_task_change', args=[obj.task.id])
            return format_html('<a href="{}" class="view-link">🔗 {} тапсырмасына өту</a>', url, obj.task.get_task_type_display())
        return '— тапсырмамен байланыспаған'

    task_link.short_description = 'Тапсырмаға сілтеме'


@admin.register(Question)
class QuestionAdmin(SummernoteModelAdmin):
    list_filter = ('test', )
    search_fields = ('test__title', )
    ordering = ('order',)
    readonly_fields = ('test_link', )
    inlines = (OptionTab, )

    def test_link(self, obj):
        if obj.test:
            url = reverse('admin:core_test_change', args=[obj.test.id])
            return format_html('<a href="{}" class="view-link">🔗 {} тестіне өту</a>', url, obj.test)
        return '— сұрақпен байланыспаған'

    test_link.short_description = 'Сұраққа сілтеме'


# Task type:Matching admin
# ----------------------------------------------------------------------------------------------------------------------
class PairTab(admin.TabularInline):
    model = Pair
    extra = 0


@admin.register(Matching)
class MatchingAdmin(SummernoteModelAdmin):
    readonly_fields = ('task_link',)
    inlines = (PairTab, )

    def task_link(self, obj):
        if obj.task:
            url = reverse('admin:core_task_change', args=[obj.task.id])
            return format_html('<a href="{}" class="view-link">🔗 {} тапсырмасына өту</a>', url, obj.task.get_task_type_display())
        return '— тапсырмамен байланыспаған'

    task_link.short_description = 'Тапсырмаға сілтеме'


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
