from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from core.models import Content, Video


# Content admin
# ----------------------------------------------------------------------------------------------------------------------
# Video Tab
class VideoTab(admin.TabularInline):
    model = Video
    fields = ('order', 'url', 'duration', )
    extra = 0


# Content admin
@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'content_type', 'order', 'view_link', )
    readonly_fields = ('view_link', )
    inlines = (VideoTab, )

    def view_link(self, obj):
        if obj.lesson:
            url = reverse('admin:core_lesson_change', args=[obj.lesson.id])
            return format_html('<a href="{}" class="view-link">🔗 {} пәніне өту</a>', url, obj.lesson.title)
        return "— пән байланыспаған"

    view_link.short_description = 'Сабаққа сілтеме'
