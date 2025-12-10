from django.db import models
from django.db.models.aggregates import Sum
from django.utils.translation import gettext_lazy as _
from core.models import User


# Subject model
# ----------------------------------------------------------------------------------------------------------------------
class Subject(models.Model):
    name = models.CharField(_('Атауы'), max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects', verbose_name=_('Қолданушы'))
    poster = models.ImageField(_('Постер'), blank=True, null=True, upload_to='core/models/subject/posters')
    description = models.TextField(_('Анықтамасы'), blank=True, null=True)
    created_at = models.DateTimeField(_('Уақыты'), auto_now_add=True)
    last_update = models.DateTimeField(_('Соңғы өзгеріс'), auto_now=True)
    view = models.PositiveIntegerField(_('Қаралым'), default=0)
    cert = models.FileField(_('Сертификат'), blank=True, null=True, upload_to='core/models/subject/certs')

    def __str__(self):
        return self.name

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
    name = models.CharField(_('Атауы'), max_length=255)
    order = models.PositiveIntegerField(_('Реттілік нөмері'), default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Модуль')
        verbose_name_plural = _('Модульдер')
        ordering = ('order', )


# Lesson model
# ----------------------------------------------------------------------------------------------------------------------
class Lesson(models.Model):
    LESSON_TYPE = (
        ('lesson', _('Сабақ')),
        ('chapter', _('БЖБ')),
        ('quarter', _('ТЖБ')),
    )

    QUARTER = (
        ('1', _('1-тоқсан')),
        ('2', _('2-тоқсан')),
        ('3', _('3-тоқсан')),
        ('4', _('4-тоқсан')),
    )

    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE,
        verbose_name=_('Пән'), related_name='lessons', null=True, blank=True
    )
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE,
        verbose_name=_('Модуль'), related_name='lessons'
    )
    title = models.CharField(_('Тақырыбы'), max_length=255)
    lesson_type = models.CharField(_('Сабақ түрі'), max_length=32, choices=LESSON_TYPE, default='lesson')
    quarter = models.CharField(_('Тоқсан'), max_length=16, choices=QUARTER, default='1')
    description = models.TextField(_('Анықтамасы'), blank=True, null=True)
    date_created = models.DateTimeField(_('Date created'), auto_now_add=True)
    last_update = models.DateTimeField(_('Last update'), auto_now=True)
    lesson_number = models.PositiveIntegerField(_('Сабақтың нөмері'), default=0)
    order = models.PositiveIntegerField(_('Реттілік нөмері'), default=0)

    def __str__(self):
        return self.title[:64]

    @property
    def max_rating(self):
        return self.tasks.aggregate(total=Sum('rating'))['total'] or 0

    class Meta:
        verbose_name = _('Сабақ')
        verbose_name_plural = _('Сабақтар')
        ordering = ('order', )


# LessonDoc model
# ----------------------------------------------------------------------------------------------------------------------
class LessonDocs(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE,
        verbose_name=_('Сабақ'), related_name='docs'
    )
    title = models.CharField(_('Тақырыбы'), max_length=255)
    file = models.FileField(_('Файл'), upload_to='core/models/lesson/docs/', blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Сабақ құжаты')
        verbose_name_plural = _('Сабақ құжаттары')
