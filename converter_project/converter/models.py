from django.db import models

# Create your models here.


class Currency(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.code


class PaymentMethod(models.Model):
    short_name = models.CharField(max_length=50)
    display_name = models.CharField(null=True, max_length=50)
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name='payment_methods')


class Seller(models.Model):
    name = models.CharField(max_length=50)
    is_merchant = models.BooleanField()
    month_finish_rate = models.FloatField()
    month_orders_count = models.IntegerField()
    user_id = models.CharField(max_length=200)


class TradeType(models.Model):
    BUY = 'BUY'
    SELL = 'SEL'
    trade_types = (
        (BUY, 'Buy'),
        (SELL, 'Sell'),
    )
    trade_type = models.CharField(
        max_length=3, choices=trade_types, default=BUY)


class Offer(models.Model):
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name='offers')
    seller = models.ForeignKey(
        Seller, on_delete=models.CASCADE, related_name='offers')
    trade_type = models.ForeignKey(
        TradeType, on_delete=models.CASCADE, related_name='offers')

    price = models.FloatField()
    min_amount = models.IntegerField()
    tradable_funds = models.FloatField()
    offer_id = models.CharField(max_length=200)
