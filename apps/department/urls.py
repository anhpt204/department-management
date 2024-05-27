# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from apps.department import views, worker

urlpatterns = [
    # path('admin/department', admin.site)
    # The home page
    path("worker", worker.update_electricity, name="worker"),
    # Matches any html file
    # re_path(r'^.*\.*', views.pages, name='pages'),
]
