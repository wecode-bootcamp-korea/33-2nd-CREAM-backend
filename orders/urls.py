from django.urls import path

from .views import OrderListView

urlpatterns = [
    path('/<int:product_id>/orders', OrderListView.as_view()),
]
