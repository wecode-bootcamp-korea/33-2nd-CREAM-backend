import json

from django.http      import JsonResponse
from django.views     import View
from django.db.models import Q, Max, Min

from core.utils      import login_decorator
from .models         import BidTypeEnum, Bid
from products.models import ProductSize

class BidView(View):
    def get(self, request, product_id):
        bid_type = request.GET.get('type')

        products = ProductSize.objects.filter(product_id=product_id)
        if not products.exists():
            return JsonResponse({'message': 'PRODUCT_SIZE_NOT_EXIST'}, status=404)

        if bid_type == 'buy':
            products = products\
                .annotate(price=Min("bids__price", filter=Q(bids__type_id=BidTypeEnum.SELL.value)))
        elif bid_type == 'sell':
            products = products\
                .annotate(price=Max("bids__price", filter=Q(bids__type_id=BidTypeEnum.BUY.value)))
        else:
            return JsonResponse({'message': 'BID_TYPE_ERROR'}, status=404)

        bid_list = [{
            'product_size_id': product.id,
            'size_name'      : product.size.name,
            'price'          : int(product.price) if product.price else None,
        } for product in products.select_related('size').prefetch_related('bids')]

        return JsonResponse({'bid_list': bid_list}, status=200)

    @login_decorator
    def post(self, request, product_id):
        try:
            user      = request.user
            bid_type  = request.GET.get('type')
            data      = json.loads(request.body)
            size_name = data['size_name']
            bid_price = data['price']

            bid_type_set = {
                'buy' : BidTypeEnum.BUY.value,
                'sell': BidTypeEnum.SELL.value
            }
            type_id = bid_type_set.get(bid_type)

            if not type_id:
                return JsonResponse({'message': 'BID_TYPE_ERROR'}, status=404)

            product_size_id = ProductSize.objects.get(size__name=size_name, product_id=product_id).id

            Bid.objects.create(
                user_id         = user.id,
                type_id         = type_id,
                product_size_id = product_size_id,
                price           = bid_price,
            )
            return JsonResponse({'message': 'BID_SUCCESS'}, status=201)

        except ProductSize.DoesNotExist:
            return JsonResponse({'message': 'PRODUCT_SIZE_NOT_EXIST'}, status=404)

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'JSON_DECODE_ERROR'}, status=400)