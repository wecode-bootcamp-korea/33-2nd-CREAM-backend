import json

from django.http      import JsonResponse
from django.views     import View
from django.db        import transaction
from django.db.models import Q, Max, Min

from core.utils      import login_decorator
from .models         import Order
from products.models import ProductSize, Product
from orders.models   import BidTypeEnum, OrderStatusEnum, Bid, Order

class OrderListView(View):
    def get(self, request, product_id):
        start_date = request.GET.get('start_date')
        end_date   = request.GET.get('end_date')
        
        orders = Order.objects.filter(product_size__product_id=product_id).order_by('-created_at')

        results = [{
            'id'         : order.id,
            'size'       : order.product_size.size.name,
            'price'      : int(order.price),
            'created_at' : order.created_at.strftime('%y/%m/%d')
        } for order in orders]

        return JsonResponse({'orders': results}, status=200)

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

class OrderView(View):
    @login_decorator
    def post(self, request, product_id):
        try:
            user       = request.user
            order_type = request.GET.get('type')
            data       = json.loads(request.body)
            size_name  = data['size_name']

            if (order_type != 'buy') and (order_type != 'sell'):
                return JsonResponse({"message": "ORDER_TYPE_ERROR"}, status=400)

            product_size_id = ProductSize.objects.get(size__name=size_name, product_id=product_id).id

            bid_type_id_set = {
                'buy' : BidTypeEnum.SELL.value,
                'sell': BidTypeEnum.BUY.value
            }
            bid_type_id = bid_type_id_set.get(order_type)

            product = Product.objects.annotate(
                buy_now_price = Min("productsize__bids__price",
                    filter=Q(productsize__bids__type_id=BidTypeEnum.SELL.value) &
                           Q(productsize__bids__product_size_id=product_size_id)
                            ),
                sell_now_price = Max("productsize__bids__price",
                    filter=Q(productsize__bids__type_id=BidTypeEnum.BUY.value) &
                           Q(productsize__bids__product_size_id=product_size_id)
                            ),
            ).get(id=product_id)
            
            price = product.buy_now_price if order_type == 'buy' else product.sell_now_price

            bid = Bid.objects.filter(
                product_size_id=product_size_id, type_id=bid_type_id, price=price).order_by('created_at')
            if not bid.exists():
                return JsonResponse({"message": "BID_NOT_EXIST"}, status=404)
            bid = bid.first()

            buyer  = request.user if order_type == 'buy' else bid.user
            seller = request.user if order_type == 'sell' else bid.user

            if buyer.point < price:
                return JsonResponse({"message": "NOT_ENOUGH_POINT"}, status=400)

            with transaction.atomic():
                Order.objects.create(
                    buyer_id        = buyer.id,
                    seller_id       = seller.id,
                    price           = price,
                    product_size_id = product_size_id,
                    status_id       = OrderStatusEnum.PREPARING.value,
                    bid_id          = bid.id,
                )
                buyer.point  -= int(price)
                seller.point += int(price)
                bid.type_id   = BidTypeEnum.END.value

                buyer.save()
                seller.save()
                bid.save()

                return JsonResponse({'message': 'ORDER_SUCCESS'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'JSON_DECODE_ERROR'}, status=400) 

        except ProductSize.DoesNotExist:
            return JsonResponse({'message': 'PRODUCT_SIZE_NOT_EXIST'}, status=404)

        except Product.DoesNotExist:
            return JsonResponse({'message': 'PRODUCT_NOT_EXIST'}, status=404) 

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)

        except transaction.TransactionManagementError:
            return JsonResponse({'message': 'TRANSACTION_MANAGEMENT_ERROR'}, status=401)          
