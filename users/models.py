from django.db import models

from core.models import TimeStampedModel

class User(TimeStampedModel):
    kakao_id           = models.BigIntegerField(unique=True)
    email              = models.EmailField(max_length=100, unique=True)
    nickname           = models.CharField(max_length=50)
    thumbnail_url      = models.URLField(max_length=600)
    point              = models.PositiveIntegerField(default=10000000)
    shoe_size          = models.CharField(max_length=20, null=True)
    address            = models.CharField(max_length=200, null=True)
    email_subscription = models.BooleanField(default=False)
    sms_subscription   = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.nickname