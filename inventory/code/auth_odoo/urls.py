from django.conf.urls import url
from django.contrib import admin
import django.contrib.auth.views as auth_views

urlpatterns = [
	# url(r'^', auth_views.login, name="auth_views.login"),
    url(r'^login/$', auth_views.login, name="auth_views.login"),
    url(r'^logout/$', auth_views.logout, name="auth_views.logout"),
    url(r'^password_change/$', auth_views.password_change, name='password_change'),
    url(r'^password_change/done/$', auth_views.password_change_done, name='password_change_done'),
    url(r'^password_reset/$', auth_views.password_reset, name='auth_views.password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
]
