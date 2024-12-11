# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "21 Thịnh Quang"
admin.site.site_title = "21 Thinh Quang"
admin.site.index_title = ""

urlpatterns = [
    path("home/", admin.site.urls),  # Django admin route
    # path("", include("apps.authentication.urls")),  # Auth routes - login / register
    # path("home/", include("apps.home.urls")),  # UI Kits Html files
    path("department/", include("apps.department.urls")),
]
