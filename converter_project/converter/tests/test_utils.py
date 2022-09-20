from unittest.mock import patch

from django.test import TestCase

from ..exceptions import BinanceApiError, OffersNotFoundError
from ..models import Currency, Offer, PaymentMethod, Seller, TradeType
from ..utils.json_parser import (get_offers_from_json,
                                 get_payment_methods_from_json)
from ..utils.offers_utils import (get_amount, get_best_offers_lists,
                                  get_best_price)


class JsonParserTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lowest_order_price = '59.79'
        cls.highest_order_price = '60.20'
        cls.failed_error_message = (
            'Dear User, this payment method is'
            ' unsupported on Binance P2P. You can still buy and sell'
            " cryptocurrency on our official partner's platform"
            ' https://www.pexpay.com/en'
        )
        cls.empty_error_message = 'Offers not found.'

        cls.currency_rub = Currency.objects.create(
            code='RUB',
            name='Russia Ruble',
        )

        cls.top_seller = Seller(
            name='NONSTOPVV',
            is_merchant=False,
            month_finish_rate=1.0*100,
            month_orders_count=29,
            user_id='sddcd03dd80483ec6ab34b7bd5b1427c5',
        )
        cls.top_offer = Offer(
            currency=cls.currency_rub,
            seller=cls.top_seller,
            trade_type=TradeType.SELL,
            price=59.79,
            min_amount=10000,
            tradable_funds=350.15,
            offer_id='11395350491045543936',
        )
        cls.test_data_path_rub = (
            'converter/tests/test_data/SELL_10_records_RUB_mixed.json')
        cls.test_data_path_try = (
            'converter/tests/test_data/BUY_10_records_TRY_mixed.json')
        cls.fail_response_path = (
            'converter/tests/test_data/fail_method_unavailable.json')
        cls.empty_response_path = (
            'converter/tests/test_data/fail_with_success_true.json')

        with open(cls.test_data_path_rub, 'r') as file:
            cls.rub_json_response = file.read()

        with open(cls.fail_response_path, 'r') as file:
            cls.fail_response = file.read()

        with open(cls.empty_response_path, 'r') as file:
            cls.empty_response = file.read()

    def assert_seller(self, seller_to_check: Seller):
        """Assert seller is test seller."""
        self.assertEqual(self.top_seller.name, seller_to_check.name)
        self.assertEqual(self.top_seller.is_merchant,
                         seller_to_check.is_merchant)
        self.assertEqual(self.top_seller.month_finish_rate,
                         seller_to_check.month_finish_rate)
        self.assertEqual(self.top_seller.month_orders_count,
                         seller_to_check.month_orders_count)
        self.assertEqual(self.top_seller.user_id, seller_to_check.user_id)

    def assert_offer(self, offer_to_check: Offer):
        """Assert offer is test offer."""
        self.assertEqual(self.top_offer.currency, offer_to_check.currency)
        self.assertEqual(self.top_offer.trade_type, offer_to_check.trade_type)
        self.assertEqual(self.top_offer.price, offer_to_check.price)
        self.assertEqual(self.top_offer.min_amount, offer_to_check.min_amount)
        self.assertEqual(self.top_offer.tradable_funds,
                         offer_to_check.tradable_funds)
        self.assertEqual(self.top_offer.offer_id,
                         offer_to_check.offer_id)

    def test_get_payment_methods(self):
        """Payment methods parsed from JSON successfully."""
        parsed_payment_methods = get_payment_methods_from_json(
            self.rub_json_response)
        self.assertEqual(PaymentMethod.objects.count(),
                         len(parsed_payment_methods))

        self.assertTrue(
            PaymentMethod.objects.filter(
                short_name='Advcash',
                display_name='Advcash',
                currency=self.currency_rub,
            ).exists()
        )

    def test_parse_offers(self):
        """Offers parsed from JSON successfully."""
        offers = get_offers_from_json(self.rub_json_response, TradeType.SELL)
        self.assertEqual(len(offers), 10)
        offers_buy = get_offers_from_json(
            self.rub_json_response, TradeType.BUY)
        top_buy_offer: Offer = offers_buy[0]

        self.assertEqual(top_buy_offer.currency,
                         self.top_offer.currency)
        self.assert_seller(top_buy_offer.seller)
        self.assert_offer(top_buy_offer)

    def test_parse_offers_correct_sorting(self):
        """Buy ans sell offers ordered correctly."""
        offers_sell = get_offers_from_json(
            self.rub_json_response, TradeType.SELL)
        offers_buy = get_offers_from_json(
            self.rub_json_response, TradeType.BUY)
        self.assertEqual(offers_sell[0].price, float(self.highest_order_price))
        self.assertEqual(offers_buy[0].price, float(self.lowest_order_price))

    def test_failed_response(self):
        """Raise BinanceApiError if request failed."""
        with self.assertRaises(BinanceApiError,
                               msg=self.failed_error_message) as exc:
            get_payment_methods_from_json(self.fail_response)
        self.assertEqual(str(exc.exception), self.failed_error_message)

        with self.assertRaises(BinanceApiError,
                               msg=self.failed_error_message) as exc:
            get_offers_from_json(self.fail_response, TradeType.SELL)
        self.assertEqual(str(exc.exception), self.failed_error_message)

    def test_empty_response(self):
        """Raise OffersNotFoundError if response is empty."""
        with self.assertRaises(OffersNotFoundError,
                               msg=self.failed_error_message) as exc:
            get_payment_methods_from_json(self.empty_response)
        self.assertEqual(str(exc.exception), self.empty_error_message)
        with self.assertRaises(OffersNotFoundError,
                               msg=self.failed_error_message) as exc:
            get_offers_from_json(self.empty_response, TradeType.SELL)
        self.assertEqual(str(exc.exception), self.empty_error_message)


class UtilsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_offers = []
        cls.seller = Seller(
            name='TestSeller',
            is_merchant=True,
            month_finish_rate=99.9,
            month_orders_count=1000,
            user_id='test_seller_id',
        )
        cls.currency_rub = Currency.objects.create(
            code='RUB',
            name='Russia Ruble',
        )
        cls.currency_try = Currency.objects.create(
            code='TRY',
            name='Turkish Lira',
        )
        cls.payment_method_rub = PaymentMethod.objects.create(
            short_name='TinkoffNew',
            display_name='Tinkoff',
            currency=cls.currency_rub,
        )
        cls.payment_method_try = PaymentMethod.objects.create(
            short_name='Ziraat',
            display_name='Ziraat',
            currency=cls.currency_try,
        )
        cls.amount_rub = 2000
        cls.is_merchant = True
        cls.is_to_amount_filled = False
        cls.best_rub_price = 59.79
        cls.best_try_price = 18.35
        cls.num_of_offers = 10
        cls.unknown_amount = (
            cls.amount_rub/cls.best_rub_price*cls.best_try_price)

        cls.test_data_path_rub = (
            'converter/tests/test_data/SELL_10_records_RUB_mixed.json')
        cls.test_data_path_try = (
            'converter/tests/test_data/BUY_10_records_TRY_mixed.json')

        with open(cls.test_data_path_rub, 'r') as file:
            cls.rub_json_response = file.read()

        with open(cls.test_data_path_try, 'r') as file:
            cls.try_json_response = file.read()

        cls.side_effect = [cls.rub_json_response,
                           cls.try_json_response,
                           cls.try_json_response, ]

        cls.try_offers_data = get_offers_from_json(cls.try_json_response,
                                                   TradeType.SELL)

        for i in range(15):
            offer = Offer(
                currency=cls.currency_rub,
                seller=cls.seller,
                trade_type=TradeType.BUY,
                price=0+i,
                min_amount=0+i,
                tradable_funds=1000+i,
                offer_id=f'offer_id_{i}',
            )
            cls.test_offers.append(offer)

    def test_get_best_price(self):
        """Price of top order returned successfully."""
        best_price = get_best_price(self.test_offers)
        self.assertEqual(best_price, self.test_offers[0].price)

    def test_get_best_offers_lists(self):
        """Return 2 lists of BUY and SELL offers, sorted correctly."""
        with patch('converter.utils.offers_utils.get_p2p_offers_data'
                   ) as get_p2p_offers_data:
            get_p2p_offers_data.side_effect = self.side_effect
            list_try, list_rub = get_best_offers_lists(
                self.currency_rub,
                self.currency_try,
                self.payment_method_rub,
                self.payment_method_try,
                self.is_merchant,
                self.amount_rub,
                self.is_to_amount_filled)
            self.assertEqual(len(list_rub), self.num_of_offers)
            self.assertEqual(len(list_try), self.num_of_offers)
            self.assertEqual((list_rub[0].price), self.best_rub_price)
            self.assertEqual((list_try[0].price), self.best_try_price)
            self.assertEqual((list_rub[0].trade_type), TradeType.SELL)
            self.assertEqual((list_try[0].trade_type), TradeType.BUY)

    def test_get_amount(self):
        """Return amount of currency_2 needed to buy currency_1."""
        amount = get_amount(
            self.amount_rub,
            self.best_rub_price,
            self.try_offers_data
        )
        self.assertEqual(amount, self.unknown_amount)
