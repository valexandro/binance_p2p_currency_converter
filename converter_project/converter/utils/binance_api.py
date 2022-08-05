"""Methods to work with Binance api."""
import requests


def get_p2p_offers_data(fiat: str,
                        is_merchant: bool = False,
                        payment_method: str = None,
                        trans_amount: int = None,
                        trade_type: str = 'BUY',
                        rows: int = 10) -> str:
    """Make request to binance p2p api.

    Args:
        is_merchant (bool): is seller certified merchant
        payment_method (PaymentMethod): Payment method for selected currency
        trans_amount (int): Amount of fiat currency to buy or sell
        fiat (Currency): Fiat currency to buy or sell
        trade_type (str): BUY or SELL, BUY means buy USDT from seller

    Returns:
        response text (str): JSON response text
    """
    data = {
        'page': 1,
        'rows': rows,
        'payTypes': [payment_method] if payment_method else [],
        'countries': [],
        'publisherType': 'merchant' if is_merchant else None,
        'transAmount': trans_amount,
        'asset': 'USDT',
        'fiat': fiat,
        'tradeType': trade_type,
    }

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'lang': 'en',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '146',
        'content-type': 'application/json',
        'Host': 'p2p.binance.com',
        'Origin': 'https://p2p.binance.com',
        'Pragma': 'no-cache',
        'TE': 'trailers',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0',
    }
    response = requests.post(
        'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search',
        headers=headers,
        json=data)
    return response.text
