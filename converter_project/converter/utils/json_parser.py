import json

from ..models import Currency, PaymentMethod


def parse_payment_methods(path: str):
    json_array = json.load(open(path))
    raw_offers = json_array['data']

    for raw_offer in raw_offers:
        trade_methods = raw_offer['adv']['tradeMethods']
        currency = raw_offer['adv']['fiatUnit']
        for trade_method in trade_methods:
            PaymentMethod.objects.update_or_create(
                short_name=trade_method['identifier'],
                display_name=trade_method['tradeMethodName'],
                currency=Currency.objects.get(code=currency)
            )
