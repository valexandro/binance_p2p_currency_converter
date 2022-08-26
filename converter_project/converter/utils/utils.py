"""Utility methods for processing offers."""
from typing import List, Tuple

from ..models import Offer, TradeType
from .binance_api import get_p2p_offers_data
from .json_parser import get_offers_from_json


def get_best_price(offers: List[Offer]) -> float:
    """Get best price of currency in list of orders.

    Orders already sorted after request.
    """
    return offers[0].price


def offers_request(currency, payment_method, is_merchant, trade_type,
                   amount=None) -> str:
    """Get list of orders from response data.

    If amount not filled, ret only one request for approximate price.
    """
    return get_offers_from_json(get_p2p_offers_data(
        currency.code,
        is_merchant,
        payment_method.short_name,
        amount,
        trade_type=trade_type,
        rows=1 if amount is None else 10,
    ), offer_type=trade_type)


def get_best_offers(currency_1, currency_2, payment_method_1, payment_method_2,
                    is_merchant, amount_1, filled_amount
                    ) -> Tuple[List[Offer], List[Offer]]:
    """Get 2 lists of best offers for both currencies.

    Process:
    First request gets best offers for currency with filled amount.
    Second request gets approximate price of second currency.
    Than based of amount of USDT needed, calculates amount of second currency.
    Final request gets best offers for second currency with calculated amount.
    """
    offers_1 = offers_request(
        currency_1, payment_method_1, is_merchant,
        TradeType.SELL if filled_amount == 'to_amount' else TradeType.BUY,
        amount_1)

    offers_2_pass_1 = offers_request(
        currency_2, payment_method_2, is_merchant,
        TradeType.BUY if filled_amount == 'to_amount' else TradeType.SELL)
    price_1 = get_best_price(offers_1)

    usdt_to_sell = amount_1/price_1
    price_2_pass_1 = get_best_price(offers_2_pass_1)
    amount_2 = price_2_pass_1 * usdt_to_sell

    offers_2_pass_2 = offers_request(
        currency_2, payment_method_2, is_merchant,
        TradeType.BUY if filled_amount == 'to_amount' else TradeType.SELL,
        amount_2)
    return offers_2_pass_2, offers_1
