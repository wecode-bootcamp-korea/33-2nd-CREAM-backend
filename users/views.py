import jwt

from django.http  import JsonResponse
from django.views import View
from django.conf  import settings

from users.models import User
from core.utils   import KakaoLoginAPI

class KakaoLoginView(View):
    def get(self, request):
        try:
            code      = request.GET.get('code')
            kakao_api = KakaoLoginAPI(client_id=settings.CLIENT_ID)

            kakao_api.get_kakao_token(code)
            kakao_profile = kakao_api.get_kakao_profile()

            user, is_created  = User.objects.get_or_create(
                kakao_id = kakao_profile['id'],
                defaults = {
                    'email'         : kakao_profile['email'],
                    'nickname'      : kakao_profile['nickname'],
                    'thumbnail_url' : kakao_profile['thumbnail_image_url']
                }
            )

            access_token = jwt.encode({'id': user.id}, settings.SECRET_KEY, settings.ALGORITHM)

            return JsonResponse({'access_token': access_token}, status=200)

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)
