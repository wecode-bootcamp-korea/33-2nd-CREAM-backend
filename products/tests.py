from django.test import TestCase, Client

from products.models import Product, ProductCategory, ProductImage, ProductSize, Size
from orders.models   import Bid, BidType, OrderStatus, Order
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
        User.objects.create(id=2, kakao_id=456, email="test2@test.com", nickname="nick", thumbnail_url="http://test.com")
        BidType.objects.create(id=1, name="테스트")
        BidType.objects.create(id=2, name="테스트")
        Bid.objects.create(id=1, user_id=1, type_id=2, product_size_id=1, price=1000)
        Bid.objects.create(id=2, user_id=1, type_id=1, product_size_id=1, price=1000)
        OrderStatus.objects.create(id=1, name="테스트")
        Order.objects.create(id=1, bid_id=1, seller_id=1, buyer_id=2, product_size_id=1, price=1000, status_id=1)
    
    def tearDown(self):
        ProductCategory.objects.all().delete()
        Product.objects.all().delete()
        ProductImage.objects.all().delete()
        Size.objects.all().delete()
        ProductSize.objects.all().delete()
        User.objects.all().delete()
        BidType.objects.all().delete()
        Bid.objects.all().delete()
        OrderStatus.objects.all().delete()
        Order.objects.all().delete()

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
    
    def test_fail_get_product_list(self):
        response = self.client.get('/products?category=6')

        self.assertEqual(response.json(),
        { 
            "product_list": []
        }
        )

    def test_success_get_product_detail(self):
        response = self.client.get('/products/1')

        self.assertEqual(response.json(),
        {
            'detail': {
                'id'            : 1,
                'eng_name'      : 'test',
                'kor_name'      : '테스트',
                'model_number'  : 'test',
                'release_date'  : '2022-01-01',
                'recent_price'  : '1,000',
                'release_price' : '1,000',
                'buy_now_price' : '1,000',
                'sell_now_price': '1,000',
                'image_list'    : ['http://test.com'],
            }
        }
        )

    def test_fail_get_product_detail(self):
        response = self.client.get('/products/50')

        self.assertEqual(response.json(),
        {
            "message": "PRODUCT_NOT_EXIST"
        }
        )

    def test_success_get_product_detail_graph(self):
        response = self.client.get('/products/1/orders')

        self.assertEqual(response.json(),
        {
            'orders': [{
                'id'        : 1,
                'size'      : '250',
                'price'     : 1000,
                'created_at': '22/06/15',
            }]
        }
        )
    
    def test_fail_get_product_detail_graph(self):
        response = self.client.get('/products/50/orders')

        self.assertEqual(response.json(),
        {
            "orders": []
        }
        )