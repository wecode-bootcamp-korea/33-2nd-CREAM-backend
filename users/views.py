import jwt

from django.http  import JsonResponse
from django.views import View
from django.conf  import settings

from users.models import User
from core.utils   import KakaoLoginAPI

class KakaoLoginView(View):
    def get(self, request):
        try:
            code            = request.GET.get('code')
            kakao_login_api = KakaoLoginAPI()

            kakao_token   = kakao_login_api.get_kakao_token(code)['access_token']
            kakao_profile = kakao_login_api.get_kakao_profile(kakao_token)

            user, is_created  = User.objects.get_or_create(
                kakao_id = kakao_profile['id'],
                defaults = {
                    'email'         : kakao_profile['kakao_account']['email'],
                    'nickname'      : kakao_profile['kakao_account']['profile']['nickname'],
                    'thumbnail_url' : kakao_profile['kakao_account']['profile']['thumbnail_image_url']
                }
            )

            cream_token = jwt.encode({'id': user.id}, settings.SECRET_KEY, settings.ALGORITHM)
            status      = 201 if is_created else 200
            return JsonResponse({'cream_token': cream_token}, status=status)

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)
