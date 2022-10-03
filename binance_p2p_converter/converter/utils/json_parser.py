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
        logger.error(json_array['message'])
        raise BinanceApiError(json_array['message'])

    raw_offers = json_array['data']

    if not raw_offers:
        logger.error('response.data is empty')
        raise OffersNotFoundError('Offers not found.')

    counter = 0
    for raw_offer in raw_offers:
        offer_data = raw_offer['adv']
        trade_methods = offer_data['tradeMethods']
        currency: Currency = get_object_or_404(
            Currency,
            code=offer_data['fiatUnit'])
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
        logger.error(json_array['message'])
        raise BinanceApiError(json_array['message'])

    raw_offers = json_array['data']

    if not raw_offers:
        logger.error('response.data is empty')
        raise OffersNotFoundError('Offers not found.')

    if offer_type == TradeType.BUY:
        logger.debug('sorting payment methods ascending')
        raw_offers.sort(key=lambda x: x['adv']['price'])
    else:
        logger.debug('sorting payment methods descending')
        raw_offers.sort(key=lambda x: x['adv']['price'], reverse=True)

    offers: List[Offer] = []

    for raw_offer in raw_offers:
        seller_data = raw_offer['advertiser']
        seller: Seller = Seller(
            name=seller_data['nickName'],
            is_merchant=(
                True if seller_data['userType'] == 'merchant'
                else False),
            month_finish_rate=float(
                seller_data['monthFinishRate'])*100,
            month_orders_count=float(
                seller_data['monthOrderCount']),
            user_id=seller_data['userNo']
        )
        offer_data = raw_offer['adv']
        offer = Offer(
            currency=get_object_or_404(
                Currency,
                code=offer_data['fiatUnit']),
            seller=seller,
            trade_type=(
                TradeType.BUY if offer_data['tradeType'] == 'BUY'
                else TradeType.SELL),
            price=float(offer_data['price']),
            min_amount=float(offer_data['minSingleTransAmount']),
            tradable_funds=float(offer_data['surplusAmount']),
            offer_id=offer_data['advNo'],
        )
        offers.append(offer)
    logger.debug(f'parsed {len(offers)} offers')
    return offers
