from dataclasses import dataclass
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


@dataclass
class Seller():
    """Seller who offer currency conversion service."""

    name: str
    is_merchant: bool
    month_finish_rate: float
    month_orders_count: int
    user_id: str

    def __str__(self) -> str:
        return f'{self.name} {self.month_finish_rate}'


class TradeType():
    """Buy means buy USDT from seller."""

    BUY = 'BUY'
    SELL = 'SELL'


@dataclass
class Offer():
    """Offer for currency conversion."""

    currency: Currency
    seller: Seller
    trade_type: TradeType
    price: float
    min_amount: int
    tradable_funds: float
    offer_id: str

    def __str__(self) -> str:
        return f'{self.seller} {self.price}'
