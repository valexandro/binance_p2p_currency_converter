from dataclasses import dataclass

from django.db import models


class Currency(models.Model):
    """Fiat currency to convert."""

    code = models.CharField(
        max_length=10,
        verbose_name='Currency Code',
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Currency',
    )

    class Meta:
        verbose_name: str = 'Currency'
        verbose_name_plural: str = 'Currencies'

    def __str__(self) -> str:
        return self.code


class PaymentMethod(models.Model):
    """Payment methods available for currency conversion."""

    short_name = models.CharField(
        max_length=50,
        verbose_name='Payment Method Identifier',
    )
    display_name = models.CharField(
        null=True,
        max_length=50,
        verbose_name='Payment Method Name',
    )
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE,
        related_name='payment_methods',
        verbose_name='Payment Method Currency',
    )
    date_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Payment Method Create/Update Date',
    )

    class Meta:

        verbose_name: str = 'Payment Method'
        verbose_name_plural: str = 'Payment Methods'

    def __str__(self) -> str:
        if self.display_name:
            return self.display_name
        return self.short_name


@dataclass
class Seller():
    """Seller who offer currency conversion service."""

    name: str
    is_merchant: bool
    month_finish_rate: float
    month_orders_count: float
    user_id: str

    def __str__(self) -> str:
        return self.name


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
    min_amount: float
    tradable_funds: float
    offer_id: str

    def __str__(self) -> str:
        return f'{self.trade_type} {self.currency.code} {self.price}'
