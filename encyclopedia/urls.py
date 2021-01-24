from django.urls import path

from . import views

urlpatterns = [
    path('<str:title>/edit', views.edit, name="edit"),
    path("", views.index, name="index"),
    path("new", views.new, name="new"),
    path("<str:entry>", views.entry, name="entry")
]
