from django.test import TestCase, Client

from products.models import Product, ProductCategory, ProductImage, ProductSize, Size
from orders.models   import Bid, BidType
from users.models    import User

class ProductTest(TestCase):
    def setUp(self):
        self.client = Client()
        ProductCategory.objects.create(id=1, name="테스트")
        Product.objects.create(id=1, korean_name="테스트", english_name="test",
        category_id=1, model_number="test", release_date="2022-01-01", release_price=1000)
        ProductImage.objects.create(id=1, product_id=1, image_url="http://test.com")
        Size.objects.create(id=1, name="250")
        ProductSize.objects.create(id=1, product_id=1, size_id=1)
        User.objects.create(id=1, kakao_id=123, email="test@test.com", nickname="nick", thumbnail_url="http://test.com")
        BidType.objects.create(id=2, name="테스트")
        Bid.objects.create(id=1, user_id=1, type_id=2, product_size_id=1, price=1000)
    
    def tearDown(self):
        ProductCategory.objects.all().delete()
        Product.objects.all().delete()
        ProductImage.objects.all().delete()
        Size.objects.all().delete()
        ProductSize.objects.all().delete()
        User.objects.all().delete()
        BidType.objects.all().delete()
        Bid.objects.all().delete()

    def test_success_get_product_list(self):
        response = self.client.get('/products')

        self.assertEqual(response.json(),
        {
            "product_list": [
                    {                   
                    "product_id"   : 1,
                    "eng_name"     : "test",
                    "kor_name"     : "테스트",
                    "thumbnail_url": "http://test.com",
                    "price"        : '1,000',
                    }
            ]
        }
        )