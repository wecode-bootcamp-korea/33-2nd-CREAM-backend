from django.urls import path

from .views import BidView

urlpatterns = [
    path('/<int:product_id>/bids', BidView.as_view()),
]

