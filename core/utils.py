import jwt, requests

from django.http import JsonResponse
from django.conf import settings

from users.models import User

def login_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            cream_token  = request.headers.get('Authorization')
            payload      = jwt.decode(cream_token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
            request.user = User.objects.get(id=payload['id'])

            return func(self, request, *args, **kwargs)

        except User.DoesNotExist:
            return JsonResponse({'message': 'USER_NOT_EXIST'}, status=400)
            
        except jwt.DecodeError:
            return JsonResponse({'message': 'INVALID_TOKEN'}, status=400)

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)

    return wrapper

class KakaoLoginAPI:
    def __init__(self):
        self.kakao_token_uri = "https://kauth.kakao.com/oauth/token"
        self.kakao_user_uri  = "https://kapi.kakao.com/v2/user/me"

    def get_kakao_token(self, code):
        body = {
            "grant_type"  : "authorization_code",
            "client_id"   : settings.KAKAO_REST_API_KEY,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code"        : code,
        }
        
        token_request = requests.post(self.kakao_token_uri, data=body, timeout=3)

        if not token_request.status_code == 200:
            return JsonResponse({'message': 'INVALID_RESPONSE'}, status=token_request.status_code)
        
        return token_request.json()
        
    def get_kakao_profile(self, kakao_token):
        kakao_response = requests.post(self.kakao_user_uri, \
            headers={"Authorization": f"Bearer {kakao_token}"}, timeout=3)
        
        if not kakao_response.status_code == 200:
            return JsonResponse({'message': 'INVALID_RESPONSE'}, status=kakao_response.status_code)

        return kakao_response.json()

