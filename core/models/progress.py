from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import User, Subject, Lesson, Chapter


# UserSubject model
# ----------------------------------------------------------------------------------------------------------------------
class UserSubject(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name=_('Қолданушы'), related_name="user_subjects")
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE,
        verbose_name=_('Пән'), related_name="user_subjects"
    )
    subject_score = models.PositiveSmallIntegerField(_('Пәннің жалпы бағасы (%)'), default=0)
    is_completed = models.BooleanField(_('Орындалды'), default=False)
    created_at = models.DateTimeField(_('Басталған уақыты'), auto_now_add=True)
    completed_at = models.DateTimeField(_('Орындалған уақыты'), blank=True, null=True)

    class Meta:
        unique_together = ('user', 'subject')
        verbose_name = _('Қолданушының пәні')
        verbose_name_plural = _('Қолданушының пәндері')

    def __str__(self):
        return f'{self.user} - {self.subject.title}'


# UserSubject model
# ----------------------------------------------------------------------------------------------------------------------
class UserChapter(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='user_chapters', verbose_name=_('Қолданушы')
    )
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE,
        related_name='user_chapters', verbose_name=_('Бөлім')
    )
    user_subject = models.ForeignKey(
        UserSubject, on_delete=models.CASCADE,
        related_name='user_chapters', verbose_name=_('Қолданушының пәндері')
    )
    chapter_score = models.DecimalField(_('Бөлімнің жалпы бағасы (%)'), max_digits=5, decimal_places=2, default=0)
    is_completed = models.BooleanField(_('Орындалды'), default=False)

    def __str__(self):
        return f'{self.user} - {self.chapter.subject.title}:{self.chapter.title}'

    class Meta:
        verbose_name = _('Қолданушының пән бөлімі')
        verbose_name_plural = _('Қолданушының пән бөлімдері')


# UserLesson model
# ----------------------------------------------------------------------------------------------------------------------
class UserLesson(models.Model):
    user_subject = models.ForeignKey(
        UserSubject, on_delete=models.CASCADE,
        verbose_name=_('Қолданушының пәні'), related_name="user_lessons")
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE,
        verbose_name=_('Сабақ'), related_name="user_lessons"
    )
    lesson_score = models.DecimalField(_('Сабақтың бағасы (%)'), max_digits=5, decimal_places=2, default=0)
    is_completed = models.BooleanField(_('Орындалды'), default=False)
    completed_at = models.DateTimeField(_('Орындалған уақыты'), blank=True, null=True)

    class Meta:
        unique_together = ('user_subject', 'lesson')
        verbose_name = _('Қолданушының сабағы')
        verbose_name_plural = _('Қолданушының сабақтары')

    def __str__(self):
        return f"{self.user_subject.user} - {self.lesson.title} - {'Орындалды' if self.is_completed else 'Процессте'}"
