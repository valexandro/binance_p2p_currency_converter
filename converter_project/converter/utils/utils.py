from typing import List

from ..models import Offer


def get_best_price(offers: List[Offer]):
    prices = []
    for offer in offers:
        prices.append(offer.price)
    return min(prices)
