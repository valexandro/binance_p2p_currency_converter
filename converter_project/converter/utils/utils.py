"""Utility methods for processing offers."""
import logging
from typing import List, Tuple

from ..models import Offer, TradeType
from .binance_api import get_p2p_offers_data
from .json_parser import get_offers_from_json

logger = logging.getLogger(__name__)


def get_best_price(offers: List[Offer]) -> float:
    """Get best price of currency in list of orders.

    Orders already sorted after request.
    """
    logger.debug('getting best price from list of offers')
    return offers[0].price


def offers_request(currency, payment_method, is_merchant, trade_type,
                   amount=None) -> str:
    """Get list of offers from response data.

    If amount not filled, get only one row for approximate price.
    """
    rows_for_price_request = 1
    rows_for_full_request = 10
    logger.debug(
        f'making request for {rows_for_price_request} row for approx price'
        if amount is None
        else
        f'making full request with {rows_for_full_request} rows'
    )
    try:
        return get_offers_from_json(get_p2p_offers_data(
            currency.code,
            is_merchant,
            payment_method.short_name,
            amount,
            trade_type=trade_type,
            rows=rows_for_price_request if amount is None
            else rows_for_full_request,
        ), offer_type=trade_type)
    except Exception as e:
        raise Exception(e) from e


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
    logger.debug(
        f'getting best offers pair for {currency_1.code} '
        f'and {currency_2.code}')
    logger.debug(
        f'requesting best offers for ({amount_1})'
        f'{currency_1.code}[{payment_method_1.display_name}]')
    try:
        offers_1 = offers_request(
            currency_1, payment_method_1, is_merchant,
            TradeType.SELL if filled_amount == 'to_amount' else TradeType.BUY,
            amount_1)
        logger.debug(
            f'requesting approx price for {currency_2.code}'
            f'[{payment_method_2.display_name}]')
        offers_2_pass_1 = offers_request(
            currency_2, payment_method_2, is_merchant,
            TradeType.BUY if filled_amount == 'to_amount' else TradeType.SELL)
        price_1 = get_best_price(offers_1)

        usdt_to_sell = amount_1/price_1
        price_2_pass_1 = get_best_price(offers_2_pass_1)
        amount_2 = price_2_pass_1 * usdt_to_sell
        logger.debug(
            f'requesting best offers for ({amount_2})'
            f'{currency_2.code}[{payment_method_2.display_name}]')
        offers_2_pass_2 = offers_request(
            currency_2, payment_method_2, is_merchant,
            TradeType.BUY if filled_amount == 'to_amount' else TradeType.SELL,
            amount_2)
    except Exception as e:
        raise Exception(e) from e
    return offers_2_pass_2, offers_1
