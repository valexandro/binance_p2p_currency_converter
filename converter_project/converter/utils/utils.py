from typing import List

from ..models import Offer, TradeType
from .binance_api import get_p2p_offers_data
from .json_parser import get_offers_from_json


def get_best_price(offers: List[Offer], trade_type):
    prices = []
    for offer in offers:
        prices.append(offer.price)
    return min(prices) if trade_type == TradeType.BUY else max(prices)


def offers_request(currency, payment_method, is_merchant, trade_type,
                   amount=None) -> str:
    return get_offers_from_json(get_p2p_offers_data(
        currency.code,
        is_merchant,
        payment_method.short_name,
        amount,
        trade_type=trade_type,
        rows=1 if amount is None else 10,
    ), offer_type=trade_type)


def get_best_offers(currency_1, currency_2, payment_method_1, payment_method_2,
                    is_merchant, amount_1, filled_amount):
    offers_1 = offers_request(
        currency_1, payment_method_1, is_merchant,
        TradeType.SELL if filled_amount == 'to_amount' else TradeType.BUY,
        amount_1)
    offers_2_pass_1 = offers_request(
        currency_2, payment_method_2, is_merchant,
        TradeType.BUY if filled_amount == 'to_amount' else TradeType.SELL)
    price_1 = get_best_price(
        offers_1,
        TradeType.SELL if filled_amount == 'to_amount' else TradeType.BUY)
    usdt_to_sell = amount_1/price_1
    price_2_pass_1 = get_best_price(
        offers_2_pass_1,
        TradeType.SELL if filled_amount == 'to_amount' else TradeType.BUY)
    amount_2 = price_2_pass_1 * usdt_to_sell
    offers_2_pass_2 = offers_request(
        currency_2, payment_method_2, is_merchant,
        TradeType.BUY if filled_amount == 'to_amount' else TradeType.SELL,
        amount_2)
    return offers_2_pass_2, offers_1
