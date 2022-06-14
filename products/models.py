from django.db import models

from core.models import TimeStampedModel

class ProductCategory(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'product_categories'

    def __str__(self):
        return self.name

class Product(TimeStampedModel):
    english_name  = models.CharField(max_length=100)
    korean_name   = models.CharField(max_length=100)
    category      = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    model_number  = models.CharField(max_length=50)
    release_date  = models.DateField(null=True)
    release_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.korean_name

    def get_price(self, sort):
        return format(int(self.sell_price), ',d') if sort == '-sell_price' else format(int(self.buy_price), ',d')
    
class ProductImage(models.Model):
    product   = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=600)

    class Meta:
        db_table = 'product_images'

    def __str__(self):
        return self.image_url

class Size(models.Model):
    name    = models.CharField(max_length=20)
    product = models.ManyToManyField(Product, through='productsize' , related_name='sizes')

    class Meta:
        db_table = 'sizes'

    def __str__(self):
        return self.name

class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size    = models.ForeignKey(Size, on_delete=models.CASCADE)

    class Meta:
        db_table = 'product_sizes'