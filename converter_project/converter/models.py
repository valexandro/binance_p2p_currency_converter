from django.db import models


class Currency(models.Model):
    """Fiat currency to convert."""

    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.code


class PaymentMethod(models.Model):
    """Payment methods available for currency conversion."""

    short_name = models.CharField(max_length=50)
    display_name = models.CharField(null=True, max_length=50)
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name='payment_methods')
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        if self.display_name:
            return self.display_name
        return 'Unknown payment method'


class Seller(models.Model):
    """Seller who offer currency conversion service."""

    name = models.CharField(max_length=50)
    is_merchant = models.BooleanField()
    month_finish_rate = models.FloatField()
    month_orders_count = models.IntegerField()
    user_id = models.CharField(max_length=200)


class TradeType(models.Model):
    """Buy means buy USDT from seller."""

    BUY = 'BUY'
    SELL = 'SEL'

    trade_type = models.CharField(
        max_length=3, default=BUY)


class Offer(models.Model):
    """Offer for currency conversion."""

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
