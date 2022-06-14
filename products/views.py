from django.http      import JsonResponse
from django.views     import View
from django.db.models import Q, F, Max, Min, Count

from products.models import Product
from orders.models   import Order, BidTypeEnum

class ProductListView(View):
    def get(self, request):
        category_id       = request.GET.get('category')
        search            = request.GET.get('search')
        shoe_size_list    = request.GET.getlist('shoe_size')
        apparel_size_list = request.GET.getlist('apparel_size')
        price_filter      = request.GET.get('price')
        sort              = request.GET.get('sort')
        offset            = int(request.GET.get('offset', 0))
        limit             = int(request.GET.get('limit', 8))

        q = Q()

        if category_id:
            q &= Q(category_id=category_id)

        if search:
            q &= Q(Q(korean_name__contains=search) | Q(english_name__icontains=search))

        if shoe_size_list:
            q &= Q(sizes__name__in=shoe_size_list)

        if apparel_size_list:
            q &= Q(sizes__name__in=apparel_size_list)

        if price_filter:
            price_list = price_filter.split('-')
            q &= Q(buy_price__range=(price_list[0], price_list[1]))

        sort_types = {
            'sales'       : '-sales_count',
            'premium'     : '-premium',
            'buy_now'     : 'buy_price',
            'sell_now'    : '-sell_price',
            'release_date': 'release_date',
        }    
        sort = sort_types.get(sort, '-sales_count')

        products = Product.objects \
            .annotate(
                buy_price   = Min("productsize__bids__price", filter=Q(productsize__bids__type_id=BidTypeEnum.SELL.value)),
                sell_price  = Max("productsize__bids__price", filter=Q(productsize__bids__type_id=BidTypeEnum.BUY.value)),
                premium     = F('buy_price') - F('release_price'),
                sales_count = Count('productsize__orders', distinct=True)
            ) \
            .filter(q).prefetch_related('images', 'productsize_set__bids') \
            .order_by(sort)[offset:offset+limit]

        product_list = [{
            "product_id"   : product.id,
            "eng_name"     : product.english_name,
            "kor_name"     : product.korean_name,
            "thumbnail_url": product.images.all()[0].image_url,
            "price"        : product.get_price(sort),
        } for product in products]

        return JsonResponse({"product_list": product_list}, status=200)

class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            order = Order.objects.filter(product_size__product_id=product_id).order_by('-created_at')

            recent_price = format(int(order.first().price), ',d') if order.exists() \
                else "최근 거래 없음"

            product = Product.objects.annotate(
                buy_now_price  = Min("productsize__bids__price", filter=Q(productsize__bids__type_id=BidTypeEnum.SELL.value)),
                sell_now_price = Max("productsize__bids__price", filter=Q(productsize__bids__type_id=BidTypeEnum.BUY.value)),
            ).get(id=product_id)

            detail = {
                  'id'            : product.id,
                  'eng_name'      : product.english_name,
                  'kor_name'      : product.korean_name,
                  'model_number'  : product.model_number,
                  'release_date'  : product.release_date,
                  'recent_price'  : recent_price,
                  'release_price' : format(int(product.release_price), ',d'),
                  'buy_now_price' : format(int(product.buy_now_price), ',d'),
                  'sell_now_price': format(int(product.sell_now_price), ',d'),
                  'image_list'    : [image.image_url for image in product.images.all()],
            }
            return JsonResponse({'detail': detail}, status=200)

        except Product.DoesNotExist:
            return JsonResponse({'message': 'PRODUCT_NOT_EXIST'}, status=404)