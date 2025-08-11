from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Lesson


# Task model
# ----------------------------------------------------------------------------------------------------------------------
class Task(models.Model):
    TASK_TYPE = (
        ('video', _('Видеосабақ')),
        ('written', _('Жазбаша')),
        ('text_gap', _('Толықтыру')),
        ('test', _('Тест')),
        ('matching', _('Сәйкестендіру')),
    )

    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE,
        related_name='tasks', verbose_name=_('Сабақ')
    )
    task_type = models.CharField(_('Тапсырма түрі'), choices=TASK_TYPE, default='written', max_length=32)
    task_score = models.PositiveIntegerField(_('Жалпы балл'), default=0)
    order = models.PositiveIntegerField(_('Реттілік нөмері'), default=0)

    def __str__(self):
        return self.get_task_type_display()

    class Meta:
        verbose_name = _('Тапсырма')
        verbose_name_plural = _('Тапсырмалар')
        ordering = ('order', )


# Task type: Video model
# ----------------------------------------------------------------------------------------------------------------------
class Video(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, null=True,
        verbose_name=_('Контент'), related_name='videos'
    )
    url = models.URLField(_('URL сілтеме'))
    duration = models.PositiveSmallIntegerField(_('Видео уақыт'), default=0)
    order = models.PositiveIntegerField(_('Реттілік нөмері'), default=0)

    def __str__(self):
        return f'{self.pk} - видеосабақ'

    class Meta:
        verbose_name = _('Видеосабақ')
        verbose_name_plural = _('Видеосабақтар')
        ordering = ('order', )


# Task type: Written model
# ----------------------------------------------------------------------------------------------------------------------
class Written(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE,
        related_name='written', verbose_name=_('Тапсырма')
    )
    instruction = models.TextField(_('Тапсырма'), blank=True, null=True)

    def __str__(self):
        return f'{self.pk} - жазбаша'

    class Meta:
        verbose_name = _('Жазбаша')
        verbose_name_plural = _('Жазбашалар')


# Task type: TextGap model
# ----------------------------------------------------------------------------------------------------------------------
class TextGap(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE,
        related_name='text_gaps', verbose_name=_('Сабақ')
    )
    prompt = models.TextField(_('Сөйлем (көп нүктемен)'))
    correct_answer = models.CharField(_('Дұрыс жауап'), max_length=255)

    def __str__(self):
        return f'{self.pk} - толықтыру'

    class Meta:
        verbose_name = _('Толықтыру')
        verbose_name_plural = _('Толықтырулар')


# Task type: Test model
# ----------------------------------------------------------------------------------------------------------------------
# Question model
class Question(models.Model):
    QUESTION_TYPE = (
        ('simple', _('Бір жауапты')),
        ('multiple', _('Көп жауапты')),
    )
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, null=True,
        related_name='questions', verbose_name=_('Тапсырма')
    )
    text = models.TextField(_('Сұрақ'))
    question_type = models.CharField(_('Сұрақтың түрі'), choices=QUESTION_TYPE, default='simple', max_length=32)
    order = models.PositiveIntegerField(_('Реттілік нөмері'), default=0)

    def __str__(self):
        return f'Тест: {self.pk} - сұрақ'

    class Meta:
        verbose_name = _('Сұрақ')
        verbose_name_plural = _('Сұрақтар')
        ordering = ('order', )


# Option model
class Option(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='options', verbose_name=_('Сұрақ')
    )
    text = models.TextField(_('Жауап'), blank=True, null=True)
    is_correct = models.BooleanField(_('Дұрыс жауап'), default=False)
    score = models.PositiveIntegerField(_('Балл'), default=0)

    def __str__(self):
        return f'Тест: {self.pk} - жауап'

    class Meta:
        verbose_name = _('Жауап')
        verbose_name_plural = _('Жауаптар')


# Task type: Matching model
# ----------------------------------------------------------------------------------------------------------------------
# Pair
class Pair(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, null=True,
        related_name='matching_pairs', verbose_name=_('Тапсырма')
    )
    left_item = models.CharField(_('Сол жақ'), max_length=255)
    right_item = models.CharField(_('Оң жақ'), max_length=255)

    def __str__(self):
        return f'{self.left_item} == {self.right_item}'

    class Meta:
        verbose_name = _('Сәйкестендіру')
        verbose_name_plural = _('Сәйкестендірулер')
