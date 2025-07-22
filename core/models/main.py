from django.db import models
from django.utils.translation import gettext_lazy as _


# Subject model
# ----------------------------------------------------------------------------------------------------------------------
class Subject(models.Model):
    title = models.CharField(_('Тақырыбы'), max_length=255)
    poster = models.ImageField(_('Постер'), blank=True, null=True, upload_to='core/models/subject/posters')
    description = models.TextField(_('Анықтамасы'), blank=True, null=True)
    created_at = models.DateTimeField(_('Уақыты'), auto_now_add=True)
    view = models.PositiveIntegerField(_('Қаралым'), default=0)
    cert = models.FileField(_('Сертификат'), blank=True, null=True, upload_to='core/models/subject/certs')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Пән')
        verbose_name_plural = _('Пәндер')
        ordering = ('created_at', )


# Chapter model
# ----------------------------------------------------------------------------------------------------------------------
class Chapter(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE,
        verbose_name=_('Пән'), related_name='chapters'
    )
    title = models.CharField(_('Тақырыбы'), max_length=255)
    description = models.TextField(_('Анықтамасы'), blank=True, null=True)
    order = models.PositiveIntegerField(_('Order'))

    def __str__(self):
        return f"{self.subject.title}: {self.order} - модуль: {self.title}"

    class Meta:
        verbose_name = _('Модуль')
        verbose_name_plural = _('Модульдер')


# Lesson model
# ----------------------------------------------------------------------------------------------------------------------
class Lesson(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE,
        verbose_name=_('Пән'), related_name="lessons", null=True, blank=True
    )
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE,
        verbose_name=_('Модуль'), related_name="lessons"
    )
    title = models.CharField(_('Тақырыбы'), max_length=255)
    duration = models.PositiveSmallIntegerField(_('Сабақтың уақыты (мин)'), default=0)
    order = models.PositiveIntegerField(_('Order'), default=0)

    def __str__(self):
        return f"{self.chapter.pk} - модуль: {self.chapter.title}. {self.title}"

    class Meta:
        verbose_name = _('Сабақ')
        verbose_name_plural = _('Сабақтар')
        ordering = ('order', )


# LessonDoc model
# ----------------------------------------------------------------------------------------------------------------------
class LessonDocs(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE,
        verbose_name=_('Сабақ'), related_name="docs"
    )
    title = models.CharField(_('Тақырыбы'), max_length=255)
    file = models.FileField(_('Файл'), upload_to='core/models/lesson/docs/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.lesson.title}"

    class Meta:
        verbose_name = _('Сабақ құжаты')
        verbose_name_plural = _('Сабақ құжаттары')


# TextContent model
# ----------------------------------------------------------------------------------------------------------------------
class TextContent(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE,
        verbose_name=_('Сабақ'), related_name='text_contents'
    )
    title = models.CharField(_('Тақырыбы'), max_length=255, blank=True, null=True)
    content = models.TextField(_('Мәтін'))

    def __str__(self):
        return f"ID:{self.pk} - мәтінді контент: {self.lesson.title}"

    class Meta:
        verbose_name = _('Мәтін контент')
        verbose_name_plural = _('Мәтін контенттер')


# VideoContent model
# ----------------------------------------------------------------------------------------------------------------------
class VideoContent(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE,
        verbose_name=_('Сабақ'), related_name='video_contents'
    )
    url = models.URLField(_('URL сілтеме'))
    duration = models.PositiveSmallIntegerField(_('Видео уақыт'), default=0)

    def __str__(self):
        return f"ID{self.pk} - видео контент: {self.lesson.title}"

    class Meta:
        verbose_name = _('Видео контент')
        verbose_name_plural = _('Видео контенттер')


# FrameContent model
# ----------------------------------------------------------------------------------------------------------------------
class FrameContent(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE,
        verbose_name=_('Сабақ'), related_name='frame_contents'
    )
    url = models.TextField(_('URL iframe сілтеме'))

    def __str__(self):
        return f"ID{self.pk} - фрейм контент: {self.lesson.title}"

    class Meta:
        verbose_name = _('Фрейм контент')
        verbose_name_plural = _('Фрейм контенттер')


# Task content
# ----------------------------------------------------------------------------------------------------------------------
class Task(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE,
        related_name='tasks', verbose_name=_('Сабақ')
    )
    title = models.CharField(_('Тақырыбы'), max_length=255)
    description = models.TextField(_('Тапсырма сұрақтары'), blank=True, null=True)
    total_score = models.PositiveIntegerField(_('Жалпы балл'), default=100)

    def __str__(self):
        return f"Тапсырма: {self.title} - {self.lesson.title}"

    class Meta:
        verbose_name = _('Тапсырма')
        verbose_name_plural = _('Тапсырмалар')


# Test content
# ----------------------------------------------------------------------------------------------------------------------
class Test(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE,
        related_name='tests', verbose_name=_('Сабақ')
    )
    title = models.CharField(_('Тақырыбы'), max_length=255)
    total_score = models.PositiveIntegerField(_('Жалпы балл'), default=100)

    def __str__(self):
        return (f""
                f"ID:{self.pk} тест: {self.title}. "
                f"{self.lesson.chapter.pk}-модуль. {self.lesson.chapter.title} "
                f"- {self.lesson.title}"
                f"")

    class Meta:
        verbose_name = _('Тест')
        verbose_name_plural = _('Тесттер')


# Question model
class Question(models.Model):
    test = models.ForeignKey(
        Test, on_delete=models.CASCADE,
        related_name='questions', verbose_name=_('Тест')
    )
    text = models.TextField(_('Сұрақ мәтіні'))
    order = models.PositiveIntegerField(_('Реті'), default=0)

    def __str__(self):
        return f"{self.test.title}. {self.order} - сұрақ"

    class Meta:
        verbose_name = _('Сұрақ')
        verbose_name_plural = _('Сұрақтар')
        ordering = ['order']


# Option model
class Option(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='options', verbose_name=_('Сұрақ')
    )
    text = models.TextField(_('Жауап мәтіні'), blank=True, null=True)
    is_correct = models.BooleanField(_('Дұрыс жауап'), default=False)
    score = models.PositiveIntegerField(_('Балл'), default=0)

    def __str__(self):
        return f"{self.question.test.title}. {self.question.order} - сұрақ ID:{self.pk} нұсқасы"

    class Meta:
        verbose_name = _('Жауап нұсқасы')
        verbose_name_plural = _('Жауап нұсқалары')
