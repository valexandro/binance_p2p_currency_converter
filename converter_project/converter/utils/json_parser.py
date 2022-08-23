import json
from typing import List

from ..models import Currency, Offer, PaymentMethod, Seller, TradeType


def get_fresh_payment_methods(response_text: str):
    json_array = json.load(open(response_text))
    # json_array = json.loads(response_text)
    raw_offers = json_array['data']

    for raw_offer in raw_offers:
        trade_methods = raw_offer['adv']['tradeMethods']
        currency = Currency.objects.get(code=raw_offer['adv']['fiatUnit'])
        for trade_method in trade_methods:
            PaymentMethod.objects.update_or_create(
                short_name=trade_method['identifier'],
                display_name=trade_method['tradeMethodName'],
                currency=currency
            )
    return PaymentMethod.objects.filter(
        currency=currency)


def get_offers_from_json(response_text: str, offer_type) -> List[Offer]:
    json_array = json.load(open(response_text))
    # json_array = json.loads(response_text)
    raw_offers = json_array['data']
    if offer_type == TradeType.BUY:
        raw_offers.sort(key=lambda x: x['adv']['price'])
    else:
        raw_offers.sort(key=lambda x: x['adv']['price'], reverse=True)
    offers: List[Offer] = []
    for raw_offer in raw_offers:
        seller: Seller = Seller(
            name=raw_offer['advertiser']['nickName'],
            is_merchant=(
                True if raw_offer['advertiser']['userType'] == 'merchant'
                else False),
            month_finish_rate=float(
                raw_offer['advertiser']['monthFinishRate'])*100,
            month_orders_count=float(
                raw_offer['advertiser']['monthOrderCount']),
            user_id=raw_offer['advertiser']['userNo']
        )
        offer = Offer(
            currency=Currency.objects.get(
                code=raw_offer['adv']['fiatUnit']),
            seller=seller,
            trade_type=(
                TradeType.BUY if raw_offer['adv']['tradeType'] == 'BUY'
                else TradeType.SELL),
            price=float(raw_offer['adv']['price']),
            min_amount=float(raw_offer['adv']['minSingleTransAmount']),
            tradable_funds=float(raw_offer['adv']['surplusAmount']),
            offer_id=raw_offer['adv']['advNo'],
        )
        offers.append(offer)
    return offers
