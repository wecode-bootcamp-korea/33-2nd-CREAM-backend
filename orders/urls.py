from django.urls import path

from .views import OrderListView, OrderView

urlpatterns = [
    path('/<int:product_id>/orders', OrderListView.as_view()),
    path('/<int:product_id>/orders', OrderView.as_view()),
]
