from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Lesson


# Content model
# ----------------------------------------------------------------------------------------------------------------------
class Content(models.Model):
    CONTENT_TYPE = (
        ('video', _('Видеосабақ')),
    )

    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE,
        related_name='contents', verbose_name=_('Сабақ')
    )
    content_type = models.CharField(_('Контент түрі'), choices=CONTENT_TYPE, default='video', max_length=32)
    order = models.PositiveIntegerField(_('Реттілік нөмері'), default=0)

    def __str__(self):
        return self.get_content_type_display()

    class Meta:
        verbose_name = _('Контент')
        verbose_name_plural = _('Контенттер')
        ordering = ('order', )


# Content type: Video model
# ----------------------------------------------------------------------------------------------------------------------
class Video(models.Model):
    content = models.ForeignKey(
        Content, on_delete=models.CASCADE, null=True,
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
