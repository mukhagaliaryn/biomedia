from django.urls import path
from .views import auth, account


urlpatterns = [
    # auth urls...
    path('login/', auth.login_view, name='login_view'),
    path('register/', auth.register_view, name='register_view'),
    path('logout/', auth.logout_view, name='logout_view'),

    # user urls...
    path('user/me/', account.account_view, name='account_view'),
    path('user/settings/', account.settings_view, name='settings_view'),
]
