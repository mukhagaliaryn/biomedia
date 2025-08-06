from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Task, Pair, Question, Option, UserLesson


# UserTask model
# ----------------------------------------------------------------------------------------------------------------------
class UserTask(models.Model):
    user_lesson = models.ForeignKey(
        UserLesson, on_delete=models.CASCADE,
        related_name='user_tasks', verbose_name=_('Қолданушының сабағы')
    )
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE,
        related_name='user_tasks', verbose_name=_('Тапсырма')
    )
    submitted_at = models.DateTimeField(_('Жіберілген уақыты'), auto_now_add=True)
    score = models.PositiveIntegerField(_('Бағасы'), default=0)
    is_completed = models.BooleanField(_('Орындалды'), default=False)

    class Meta:
        verbose_name = _('Тапсырма нәтижесі')
        verbose_name_plural = _('Тапсырма нәтижелері')

    def __str__(self):
        return f'{self.user_lesson.user} | {self.task}'


# UserWritten model
# ----------------------------------------------------------------------------------------------------------------------
class UserWritten(models.Model):
    user_task = models.OneToOneField(
        UserTask, on_delete=models.CASCADE,
        related_name='written_answer', verbose_name=_('Жауап')
    )
    answer = models.TextField(_('Жазған мәтіні'))

    class Meta:
        verbose_name = _('Жазбаша жауап')
        verbose_name_plural = _('Жазбаша жауаптар')


# UserTextGap model
# ----------------------------------------------------------------------------------------------------------------------
class UserTextGap(models.Model):
    user_task = models.OneToOneField(
        UserTask, on_delete=models.CASCADE,
        related_name='text_gap_answer', verbose_name=_('Жауап')
    )
    answer = models.CharField(_('Жазған жауабы'), max_length=255)
    is_correct = models.BooleanField(_('Дұрыс па'), default=False)

    class Meta:
        verbose_name = _('Сөйлемді аяқтау жауабы')
        verbose_name_plural = _('Сөйлемді аяқтау жауаптары')


# Test model
# ----------------------------------------------------------------------------------------------------------------------
# UserQuestion model
class UserQuestion(models.Model):
    user_task = models.ForeignKey(
        UserTask, on_delete=models.CASCADE,
        related_name='user_questions', verbose_name=_('Қолданушы тапсырмасы')
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='user_questions', verbose_name=_('Сұрақ')
    )
    is_correct = models.BooleanField(_('Дұрыс па'), default=False)
    score = models.PositiveIntegerField(_('Жинаған балл'), default=0)

    class Meta:
        verbose_name = _('Қолданушы сұрағы')
        verbose_name_plural = _('Қолданушы сұрақтары')


# UserAnswer model
class UserAnswer(models.Model):
    user_question = models.ForeignKey(
        UserQuestion, on_delete=models.CASCADE,
        related_name='user_answers', verbose_name=_('Қолданушы сұрағы')
    )
    options = models.ManyToManyField(Option, related_name='user_answers', verbose_name=_('Таңдалған нұсқалар'))

    class Meta:
        verbose_name = _('Таңдалған жауап')
        verbose_name_plural = _('Таңдалған жауаптар')


# UserMatching model
# ----------------------------------------------------------------------------------------------------------------------
class UserMatching(models.Model):
    user_task = models.ForeignKey(
        UserTask, on_delete=models.CASCADE,
        related_name='matching_answers', verbose_name=_('Қолданушы тапсырмасы')
    )
    pair = models.ForeignKey(
        Pair, on_delete=models.CASCADE,
        verbose_name=_('Сәйкес жұп (дұрыс)')
    )
    selected_right = models.CharField(_('Таңдалған оң жақ'), max_length=255)
    is_correct = models.BooleanField(_('Сәйкес пе?'), default=False)

    class Meta:
        verbose_name = _('Сәйкестендіру жауабы')
        verbose_name_plural = _('Сәйкестендіру жауаптары')
