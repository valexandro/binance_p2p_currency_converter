"""Package for processing offers from JSON."""
import json
import logging
from typing import List

from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404

from ..exceptions import BinanceApiError, OffersNotFoundError
from ..models import Currency, Offer, PaymentMethod, Seller, TradeType

logger = logging.getLogger(__name__)


def get_payment_methods_from_json(
        response_text: str) -> QuerySet[PaymentMethod]:
    """Parse json and create missing payment methods."""
    json_array = json.loads(response_text)
    if not json_array['success']:
        raise BinanceApiError(json_array['message'])

    raw_offers = json_array['data']

    if not raw_offers:
        raise OffersNotFoundError('Offers not found.')

    counter = 0
    for raw_offer in raw_offers:
        trade_methods = raw_offer['adv']['tradeMethods']
        currency: Currency = get_object_or_404(
            Currency,
            code=raw_offer['adv']['fiatUnit'])
        for trade_method in trade_methods:
            short_name = trade_method['identifier']
            display_name = trade_method['tradeMethodName']
            PaymentMethod.objects.update_or_create(
                short_name=short_name,
                display_name=display_name,
                currency=currency,
            )
            counter += 1
    logger.debug(f'parsed {counter} payment methods')
    return PaymentMethod.objects.filter(
        currency=currency)


def get_offers_from_json(response_text: str, offer_type) -> List[Offer]:
    """Parse json and create offers list sorted by price."""
    json_array = json.loads(response_text)
    if not json_array['success']:
        logger.error('request unsuccessful')
        raise BinanceApiError(json_array['message'])

    raw_offers = json_array['data']

    if not raw_offers:
        logger.error('request empty')
        raise OffersNotFoundError('Offers not found.')

    if offer_type == TradeType.BUY:
        logger.debug('sorting payment methods ascending')
        raw_offers.sort(key=lambda x: x['adv']['price'])
    else:
        logger.debug('sorting payment methods descending')
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
            currency=get_object_or_404(
                Currency,
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
    logger.debug(f'parsed {len(offers)} offers')
    return offers
