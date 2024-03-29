"""Utility methods for processing offers."""
import logging
from typing import List, Tuple

from ..models import Offer, TradeType
from .binance_api import get_p2p_offers_data
from .json_parser import get_offers_from_json

logger = logging.getLogger(__name__)


def get_best_price(offers: List[Offer]) -> float:
    """Get best price of currency in list of orders.

    Orders already sorted properly after parsing.
    """
    logger.debug('getting best price from list of offers')
    return offers[0].price


def get_best_offers_lists(currency_1, currency_2, payment_method_1,
                          payment_method_2, is_merchant, filled_amount,
                          is_to_amount_filled
                          ) -> Tuple[List[Offer], List[Offer]]:
    """Get 2 lists of best offers for both currencies.

    Currency 1 have amount filled. Currency 2 amount need to be found.
    Process:
    First request: gets best offers for currency with filled amount.
    Second request: gets approximate price of second currency.
    Than, based of amount of USDT needed, find amount of second currency,
    needed to make request.
    Final request: gets best offers for second currency with correct amount.
    """
    logger.debug(
        f'getting best offers pair for {currency_1.code} '
        f'and {currency_2.code}')

    rows_for_price_request = 1
    rows_for_full_request = 10
    trade_type_1 = (
        TradeType.SELL if is_to_amount_filled else TradeType.BUY)
    trade_type_2 = (
        TradeType.SELL if not is_to_amount_filled else TradeType.BUY)

    logger.debug(
        f'requesting best offers for ({filled_amount})'
        f'{currency_1.code}[{payment_method_1.display_name}]')

    try:
        offers_filled_amount_currency = (
            get_offers_from_json(
                get_p2p_offers_data(
                    fiat_code=currency_1.code,
                    is_merchant=is_merchant,
                    payment_method=payment_method_1.short_name,
                    trans_amount=filled_amount,
                    trade_type=trade_type_1,
                    rows=rows_for_full_request
                ), offer_type=trade_type_1
            )
        )
        price_filled_amount_currency = get_best_price(
            offers_filled_amount_currency)

        logger.debug(
            f'requesting approx price for {currency_2.code}'
            f'[{payment_method_2.display_name}]')

        single_offer_data_unfilled_amount_currency = (
            get_offers_from_json(
                get_p2p_offers_data(
                    fiat_code=currency_2.code,
                    is_merchant=is_merchant,
                    payment_method=payment_method_2.short_name,
                    trans_amount=None,
                    trade_type=trade_type_2,
                    rows=rows_for_price_request
                ), offer_type=trade_type_2
            )
        )
        required_amount_of_unfilled_currency = get_amount(
            filled_amount,
            price_filled_amount_currency,
            single_offer_data_unfilled_amount_currency)

        logger.debug(
            f'requesting best offers for'
            f' ({required_amount_of_unfilled_currency})'
            f'{currency_2.code}[{payment_method_2.display_name}]')

        offers_unfilled_amount_currency = (
            get_offers_from_json(
                get_p2p_offers_data(
                    fiat_code=currency_2.code,
                    is_merchant=is_merchant,
                    payment_method=payment_method_2.short_name,
                    trans_amount=required_amount_of_unfilled_currency,
                    trade_type=trade_type_2,
                    rows=rows_for_full_request,
                ), offer_type=trade_type_2
            )
        )
    except Exception as e:
        raise Exception(e) from e
    return offers_unfilled_amount_currency, offers_filled_amount_currency


def get_amount(filled_amount_1, price_1, offers_data_2) -> float:
    """Get max amount of currency 2 can be traded for set amount of currency 1.

    Buy USDT for set amount of currency 1. Than sell USDT for currency 2.
    """
    usdt_to_sell = filled_amount_1/price_1
    price_2 = get_best_price(offers_data_2)
    return price_2 * usdt_to_sell
