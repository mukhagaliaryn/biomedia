from django.contrib import admin
from core.models import UserTask, UserVideo


# UserTask admin
# ----------------------------------------------------------------------------------------------------------------------
class UserVideoTab(admin.TabularInline):
    model = UserVideo
    extra = 0


@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = ('user_lesson', 'task', 'submitted_at', 'score', 'is_completed', )
    list_filter = ('user_lesson', 'task', 'is_completed', )
    inlines = (UserVideoTab, )