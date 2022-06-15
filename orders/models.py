from django.db import models

from core.models     import TimeStampedModel
from users.models    import User
from products.models import ProductSize

class BidTypeEnum(Enum):
    BUY      = 1
    SELL     = 2
    END      = 3
    CANCELED = 4

class BidType(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        db_table = 'bid_types'

    def __str__(self):
        return self.name

class Bid(TimeStampedModel):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    type         = models.ForeignKey(BidType, on_delete=models.CASCADE, related_name='bids')
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, related_name='bids')
    price        = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'bids'

class OrderStatus(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        db_table = 'order_status'
    
    def __str__(self):
        return self.name

class Order(TimeStampedModel):
    seller       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sell_orders')
    buyer        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buy_orders')
    bid          = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name='orders')
    price        = models.DecimalField(max_digits=10, decimal_places=2)
    product_size = models.ForeignKey(ProductSize, on_delete=models.SET_NULL, null=True, related_name='orders')
    status       = models.ForeignKey(OrderStatus, on_delete=models.SET_NULL, null=True, related_name='orders')

    class Meta:
        db_table = 'orders'

