from enum import Enum

from django.http      import JsonResponse
from django.views     import View
from django.db.models import Q, F, Max, Min, Count

from products.models import Product

class BidTypeEnum(Enum):
    BUY      = 1
    SELL     = 2
    END      = 3
    CANCELED = 4

class ProductListView(View):
    def get(self, request):
        category          = request.GET.get('category')
        search            = request.GET.get('search')
        shoe_size_list    = request.GET.getlist('shoe_size')
        apparel_size_list = request.GET.getlist('apparel_size')
        price_filter      = request.GET.get('price')
        sort              = request.GET.get('sort')
        offset            = int(request.GET.get('offset', 0))
        limit             = int(request.GET.get('limit', 8))

        q = Q()

        if category:
            q &= Q(category__name=category)

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
        
        products = Product.objects.prefetch_related('images', 'productsize_set__bids')\
            .annotate(buy_price=Min("productsize__bids__price", filter=Q(productsize__bids__type_id=BidTypeEnum.SELL.value)),
            sell_price=Max("productsize__bids__price", filter=Q(productsize__bids__type_id=BidTypeEnum.BUY.value)),
            premium=F('buy_price') - F('release_price'), sales_count=Count('productsize__orders', distinct=True))\
            .filter(q).distinct().order_by(sort_types.get(sort, '-sales_count'))[offset:offset+limit]

        product_list = [{
            "product_id"   : product.id,
            "eng_name"     : product.english_name,
            "kor_name"     : product.korean_name,
            "thumbnail_url": product.images.all()[0].image_url,
            "price"        : format(int(product.sell_price), ',d') if sort == '-sell_price' \
                else format(int(product.buy_price), ',d'),
        } for product in products]

        return JsonResponse({"product_list": product_list}, status=200)