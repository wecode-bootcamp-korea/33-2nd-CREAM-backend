from django.http      import JsonResponse
from django.views import View

from .models import Order

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