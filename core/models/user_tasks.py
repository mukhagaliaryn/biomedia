from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Task, Option, UserLesson, Video, Written, TextGap, Question


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
    rating = models.PositiveSmallIntegerField(_('Жалпы бағасы'), default=0)
    is_completed = models.BooleanField(_('Орындалды'), default=False)

    class Meta:
        verbose_name = _('Қолданушының тапсырмасы')
        verbose_name_plural = _('Қолданушының тапсырмалары')

    def __str__(self):
        return f'{self.user_lesson.user} | {self.task}'


# UserVideo model
# ----------------------------------------------------------------------------------------------------------------------
class UserVideo(models.Model):
    user_task = models.ForeignKey(
        UserTask, on_delete=models.CASCADE,
        related_name='user_videos', verbose_name=_('Қолданушының тапсырмасы')
    )
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE,
        related_name='user_videos', verbose_name=_('Видеосабақ')
    )
    watched_seconds = models.PositiveIntegerField(_('Қараған уақыт (сек)'), default=0)
    is_completed = models.BooleanField(_('Аяқталған'), default=False)

    class Meta:
        verbose_name = _('Қолданушының видеосабағы')
        verbose_name_plural = _('Қолданушының видеосабақтары')


# UserWritten model
# ----------------------------------------------------------------------------------------------------------------------
class UserWritten(models.Model):
    user_task = models.ForeignKey(
        UserTask, on_delete=models.CASCADE,
        related_name='user_written', verbose_name=_('Қолданушының тапсырмасы')
    )
    written = models.ForeignKey(
        Written, on_delete=models.CASCADE, null=True,
        related_name='user_written', verbose_name=_('Жазбаша')
    )
    file = models.FileField(_('Файл'), upload_to='core/models/user_written/files/', null=True, blank=True)
    answer = models.TextField(_('Жауабы'))
    is_submitted = models.BooleanField(_('Жіберілді'), default=False)

    class Meta:
        verbose_name = _('Қолданушының жазбаша жауабы')
        verbose_name_plural = _('Қолданушының жазбаша жауаптары')


# UserTextGap model
# ----------------------------------------------------------------------------------------------------------------------
class UserTextGap(models.Model):
    user_task = models.ForeignKey(
        UserTask, on_delete=models.CASCADE,
        related_name='user_text_gaps', verbose_name=_('Қолданушының тапсырмасы')
    )
    text_gap = models.ForeignKey(
        TextGap, on_delete=models.CASCADE, null=True,
        related_name='user_text_gaps', verbose_name=_('Толықтыру')
    )
    answer = models.CharField(_('Жауабы'), max_length=255, null=True, blank=True)
    is_correct = models.BooleanField(_('Дұрыс па?'), default=False)

    class Meta:
        verbose_name = _('Қолданушының сәйкестендіруі')
        verbose_name_plural = _('Қолданушының сәйкестендірулері')


# Test model
# ----------------------------------------------------------------------------------------------------------------------
# UserAnswer model
class UserAnswer(models.Model):
    user_task = models.ForeignKey(
        UserTask, on_delete=models.CASCADE, null=True,
        related_name='user_options', verbose_name=_('Қолданушы тапсырмасы')
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, null=True,
        related_name='user_options', verbose_name=_('Жауап')
    )
    options = models.ManyToManyField(Option, related_name='user_answers', verbose_name=_('Таңдалған жауаптар'))

    class Meta:
        verbose_name = _('Таңдалған жауап')
        verbose_name_plural = _('Таңдалған жауаптар')
