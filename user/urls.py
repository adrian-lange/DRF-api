from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.UserCreateAPIView.as_view(), name="user-create"),
    path("edit/", views.UserUpdateAPIView.as_view(), name="user-edit"),
    path("delete/", views.UserDestroyAPIView.as_view(), name="user-delete"),
    path(
        "password/change/",
        views.UserPasswordUpdateAPIView.as_view(),
        name="password-change",
    ),
]
