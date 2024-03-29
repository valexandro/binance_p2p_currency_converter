# Generated by Django 4.0.6 on 2022-07-28 05:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('is_merchant', models.BooleanField()),
                ('month_finish_rate', models.FloatField()),
                ('month_orders_count', models.IntegerField()),
                ('user_id', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='TradeType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[('BUY', 'Buy'), ('SELL', 'Sell')], default='BUY')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethods',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=50)),
                ('display_name', models.CharField(max_length=50)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_methods', to='converter.currency')),
            ],
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('min_amount', models.IntegerField()),
                ('tradable_funds', models.FloatField()),
                ('offer_id', models.CharField(max_length=200)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='converter.currency')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='converter.seller')),
                ('trade_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='converter.tradetype')),
            ],
        ),
    ]
