from django.urls import path

from . import views

urlpatterns = [
    path("", views.ReceiptListCreateAPIView.as_view(), name="receipt-list"),
    path("<int:pk>/", views.ReceiptDetailAPIView.as_view(), name="receipt-detail"),
    path("<int:pk>/edit/", views.ReceiptUpdateAPIView.as_view()),
    path("<int:pk>/delete/", views.ReceiptDestroyAPIView.as_view()),
]
