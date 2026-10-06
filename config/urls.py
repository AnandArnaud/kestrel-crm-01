from django.contrib import admin
from django.urls import path

from contacts import views

urlpatterns = [
    path("", views.contact_list, name="contact-list"),
    path("api/contacts/", views.contact_list_json, name="contact-list-json"),
    path("health/", views.health, name="health"),
    path("admin/", admin.site.urls),
]
