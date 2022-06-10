from unittest.mock import patch

from django.test   import TestCase, Client

from .models    import User
from core.utils import KakaoLoginAPI

class UserTest(TestCase):
    def setUp(self):
        self.client = Client()

        User.objects.create(
            id            = 123,
            kakao_id      = 123456789,
            email         = 'test@kakao.com',
            nickname      = 'nick',
            thumbnail_url = 'http://test.com/test.jpg',
        )

    def tearDown(self):
        User.objects.all().delete()

    @patch.object(KakaoLoginAPI, "get_kakao_profile")
    @patch.object(KakaoLoginAPI, "get_kakao_token")
    def test_success_kakao_login(self, mocked_kakao_token, mocked_kakao_profile):
        class MockedToken:
            def json(self):
                return {"access_token" : "123456789"}

        class MockedKakaoProfile:
            def json(self):
                return {
                    'id': 1234,
                    'kakao_account': {
                        'email' : 'tester@kakao.com',
                        'profile': {
                            'nickname'           : 'nick',
                            'thumbnail_image_url': 'http://test.com/test.jpg'
                            }
                        }
                    }

        mocked_kakao_token.return_value   = MockedToken().json()
        mocked_kakao_profile.return_value = MockedKakaoProfile().json()
        response                          = self.client.get('/users/login/kakao')

        self.assertEqual(response.status_code, 201)

    @patch.object(KakaoLoginAPI, "get_kakao_profile")
    @patch.object(KakaoLoginAPI, "get_kakao_token")
    def test_keyerror_kakaologinview(self, mocked_kakao_token, mocked_kakao_profile):
        class MockedToken:
            def json(self):
                return {"access_token" : "123456789"}

        class MockedKakaoProfile:
            def json(self):
                return {
                    'wrong_key': 1234,
                    'kakao_account': {
                        'email' : 'tester@kakao.com',
                        }
                    }

        mocked_kakao_token.return_value   = MockedToken().json()
        mocked_kakao_profile.return_value = MockedKakaoProfile().json()
        response                          = self.client.get('/users/login/kakao')

        self.assertEqual(response.status_code, 400)