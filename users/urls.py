from django.urls import path

from .views import KakaoLoginView

urlpatterns = [
    path('/login/kakao', KakaoLoginView.as_view()),
]