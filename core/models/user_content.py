from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Video, UserLesson, Content


# UserContent model
# ----------------------------------------------------------------------------------------------------------------------
class UserContent(models.Model):
    user_lesson = models.ForeignKey(
        UserLesson, on_delete=models.CASCADE,
        related_name='user_contents', verbose_name=_('Қолданушының сабағы')
    )
    content = models.ForeignKey(
        Content, on_delete=models.CASCADE,
        related_name='user_contents', verbose_name=_('Контент')
    )
    is_completed = models.BooleanField(_('Орындалды'), default=False)

    class Meta:
        verbose_name = _('Қолданушының контенті')
        verbose_name_plural = _('Қолданушының контенттері')

    def __str__(self):
        return f'{self.user_lesson.user} | {self.content}'


# UserVideo model
# ----------------------------------------------------------------------------------------------------------------------
class UserVideo(models.Model):
    user_content = models.ForeignKey(
        UserContent, on_delete=models.CASCADE,
        related_name='user_videos', verbose_name=_('Қолданушының контенті')
    )
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE,
        related_name='user_videos', verbose_name=_('Видео')
    )
    viewed_at = models.DateTimeField(_('Көрген уақыты'), auto_now_add=True)
    watched_seconds = models.PositiveIntegerField(_('Қараған уақыт (сек)'), default=0)
    is_completed = models.BooleanField(_('Аяқталған'), default=False)

    class Meta:
        verbose_name = _('Қолданушының видеосабағы')
        verbose_name_plural = _('Қолданушының видеосабақтары')
