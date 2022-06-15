from enum import Enum

from django.http      import JsonResponse
from django.views     import View
from django.db.models import Q, F, Max, Min, Count

from products.models import Product

class ProductListView(View):
    def get(self, request):
        category_id      = request.GET.get('category_id')
        search           = request.GET.get('search')
        shoe_size_ids    = request.GET.getlist('shoe_size_ids')
        apparel_size_ids = request.GET.getlist('apparel_size_ids')
        price_filter     = request.GET.get('price')
        sort             = request.GET.get('sort')
        offset           = int(request.GET.get('offset', 0))
        limit            = int(request.GET.get('limit', 8))

        q = Q()

        if category:
            q &= Q(category_id=category_id)

        if search:
            q &= Q(Q(korean_name__contains=search) | Q(english_name__icontains=search))

        if shoe_size_ids:
            q &= Q(sizes__name__in=shoe_size_ids)

        if apparel_size_ids:
            q &= Q(sizes__name__in=apparel_size_ids)

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
            .filter(q) \
            .prefetch_related('images', 'productsize_set__bids') \
            .distinct()
            .order_by(sort)[offset:offset+limit]

        product_list = [{
            "product_id"   : product.id,
            "eng_name"     : product.english_name,
            "kor_name"     : product.korean_name,
            "thumbnail_url": product.images.all()[0].image_url,
            "price"        : product.get_price(sort_type),
        } for product in products]


        return JsonResponse({"product_list": product_list}, status=200)
