from enum import Enum

from django.db import models

from core.models     import TimeStampedModel
from products.models import ProductSize
from users.models    import User

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
