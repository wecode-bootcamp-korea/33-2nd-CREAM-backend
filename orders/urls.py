from django.urls import path

from .views import OrderListView, BidView, OrderView

urlpatterns = [
    path('/<int:product_id>/orders', OrderListView.as_view()),
    path('/<int:product_id>/bids', BidView.as_view()),
    path('/<int:product_id>/order', OrderView.as_view()),
]
