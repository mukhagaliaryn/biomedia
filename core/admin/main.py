from django.contrib import admin
from core.models import Subject, Chapter, Lesson, TextContent, VideoContent, LessonDocs, Test, Question, Option, \
    FrameContent, Task
from django_summernote.admin import SummernoteModelAdmin, SummernoteModelAdminMixin


# Subject admin
# ----------------------------------------------------------------------------------------------------------------------
class ChapterTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Chapter
    extra = 0


class LessonTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Lesson
    extra = 0


@admin.register(Subject)
class SubjectAdmin(SummernoteModelAdmin):
    list_display = ('title', 'created_at', 'view', )
    search_fields = ('title', 'description')
    inlines = (ChapterTab, LessonTab, )


# Chapter admin
# ----------------------------------------------------------------------------------------------------------------------
@admin.register(Chapter)
class ChapterAdmin(SummernoteModelAdmin):
    list_display = ('title', 'subject', 'order')
    list_filter = ('subject',)
    ordering = ('order',)
    inlines = (LessonTab, )


# Lesson admin
# ----------------------------------------------------------------------------------------------------------------------
class TextContentTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = TextContent
    extra = 0

class VideoContentTab(admin.TabularInline):
    model = VideoContent
    extra = 0


class FrameContentTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = FrameContent
    extra = 0

class TaskTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Task
    extra = 0


class FileDocTab(admin.TabularInline):
    model = LessonDocs
    extra = 0


@admin.register(Lesson)
class LessonAdmin(SummernoteModelAdmin):
    list_display = ('title', 'chapter', 'order')
    list_filter = ('subject', 'chapter', )
    ordering = ('chapter', 'order')
    inlines = (FileDocTab, TextContentTab, VideoContentTab, FrameContentTab, TaskTab, )


# Task admin
# ----------------------------------------------------------------------------------------------------------------------
# class UserTaskTab(SummernoteModelAdminMixin, admin.StackedInline):
#     model = UseTask
#     extra = 0


@admin.register(Task)
class TaskAdmin(SummernoteModelAdmin):
    list_display = ('title', 'lesson', 'total_score', )
    # inlines = (UserTaskTab, )


# Test admin
# ----------------------------------------------------------------------------------------------------------------------
class QuestionTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Question
    extra = 0


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'total_score')
    search_fields = ('title', 'lesson__title')

    inlines = (QuestionTab, )


# Option
class OptionTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Option
    extra = 0


@admin.register(Question)
class QuestionAdmin(SummernoteModelAdmin):
    list_filter = ('test', )
    search_fields = ('test__title', )
    ordering = ('order',)

    inlines = (OptionTab, )
