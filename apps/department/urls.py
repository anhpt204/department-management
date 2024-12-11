# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from apps.department import views, worker

urlpatterns = [
    # path('admin/department', admin.site)
    # The home page
    path("worker", worker.update_electricity, name="worker"),
    path("worker/update-expired-contracts", worker.update_expired_contracts, name='worker-update-expired-contract'),
    re_path(
        "invoices/(?P<invoice_pk>\d+)/$", views.show_invoice_detail, name="show_invoice"
    ),
    # Matches any html file
    # re_path(r'^.*\.*', views.pages, name='pages'),
]
