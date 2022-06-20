# Generated by Django 4.0.5 on 2022-06-20 01:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_alter_user_kakao_id'),
        ('products', '0003_rename_productcateogory_productcategory'),
    ]

    operations = [
        migrations.CreateModel(
            name='BidType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'bid_types',
            },
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('product_size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='products.productsize')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='bids.bidtype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='users.user')),
            ],
            options={
                'db_table': 'bids',
            },
        ),
    ]
