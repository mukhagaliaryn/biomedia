from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Lesson


# Task model
# ----------------------------------------------------------------------------------------------------------------------
class Task(models.Model):
    TASK_TYPE = (
        ('written', _('Жазбаша')),
        ('text_gap', _('Сөйлемді аяқтау')),
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


# Task type: Written model
# ----------------------------------------------------------------------------------------------------------------------
class Written(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE,
        related_name='written', verbose_name=_('Тапсырма')
    )
    instruction = models.TextField(_('Тапсырма'), blank=True, null=True)

    def __str__(self):
        return f'{self.pk} - жазбаша тапсырма'

    class Meta:
        verbose_name = _('Жазбаша')
        verbose_name_plural = _('Жазбаша тапсырмалар')


# Task type: TextGap model
# ----------------------------------------------------------------------------------------------------------------------
class TextGap(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE,
        related_name='text_gaps', verbose_name=_('Сабақ')
    )
    prompt = models.TextField(_('Сөйлем (көп нүктемен)'))  # "..." белгісімен жазылады
    correct_answer = models.CharField(_('Дұрыс жауап'), max_length=255)

    def __str__(self):
        return f'{self.pk} - сөйлемді аяқтау тапсырмасы'

    class Meta:
        verbose_name = _('Сөйлемді аяқтау тапсырмасы')
        verbose_name_plural = _('Сөйлемді аяқтау тапсырмалары')


# Task type: Test model
# ----------------------------------------------------------------------------------------------------------------------
class Test(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE,
        related_name='tests', verbose_name=_('Тапсырма')
    )
    instruction = models.TextField(_('Тест'), blank=True, null=True)

    def __str__(self):
        return f'{self.pk} - тест'

    class Meta:
        verbose_name = _('Тест')
        verbose_name_plural = _('Тесттер')


# Question model
class Question(models.Model):
    QUESTION_TYPE = (
        ('simple', _('Бір жауапты')),
        ('multiple', _('Көп жауапты')),
    )
    test = models.ForeignKey(
        Test, on_delete=models.CASCADE,
        related_name='questions', verbose_name=_('Тест')
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
    score = models.PositiveIntegerField(_('Жауап баллы'), default=0)

    def __str__(self):
        return f'Тест: {self.pk} - жауап'

    class Meta:
        verbose_name = _('Жауап нұсқасы')
        verbose_name_plural = _('Жауап нұсқалары')


# Task type: Matching model
# ----------------------------------------------------------------------------------------------------------------------
class Matching(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE,
        related_name='identifications', verbose_name=_('Тапсырма')
    )
    instruction = models.TextField(_('Сұрақ'), blank=True, null=True)

    def __str__(self):
        return f'{self.pk} - сәкестендіру тапсырмасы'

    class Meta:
        verbose_name = _('Сәйкестендіру')
        verbose_name_plural = _('Сәйкестендірулер')


# Pair
class Pair(models.Model):
    matching = models.ForeignKey(
        Matching, on_delete=models.CASCADE,
        related_name='pairs', verbose_name=_('Сәйкестендіру')
    )
    left_item = models.CharField(_('Сол жақ'), max_length=255)
    right_item = models.CharField(_('Оң жақ (дұрыс жауап)'), max_length=255)

    def __str__(self):
        return f'{self.left_item} -> {self.right_item}'

    class Meta:
        verbose_name = _('Сәйкестендіру жұбы')
        verbose_name_plural = _('Сәйкестендіру жұптары')
