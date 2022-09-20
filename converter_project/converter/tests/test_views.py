from http import HTTPStatus
from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from ..forms import ConverterForm
from ..models import Currency, PaymentMethod


class ConverterViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.currency_rub = Currency.objects.create(
            code='RUB',
            name='Russia Ruble',
        )
        cls.currency_try = Currency.objects.create(
            code='TRY',
            name='Turkish Lira',
        )
        cls.empty_request_response = '<option value="">---------</option>'
        cls.payment_method_not_found = (
            f'<option>Payment methods for {cls.currency_rub.code}'
            f' does not exist.</option>'
        )
        cls.test_response_rub = (
            '<option value="" selected>---------</option>'
            '<option value="1">BinancePay (RUB)</option>'
            '<option value="2">Payeer</option>'
            '<option value="3">Advcash</option>'
        )
        cls.test_response_try = (
            '<option value="" selected>---------</option>'
            '<option value="4">Eurasian Bank</option>'
            '<option value="5">Bank RBK</option>'
            '<option value="6">CenterCredit Bank</option>'
            '<option value="7">Home Credit Kazakhstan</option>'
            '<option value="8">Kaspi Bank</option>'
            '<option value="9">VakifBank</option>'
            '<option value="10">DenizBank</option>'
            '<option value="11">Kuveyt Turk</option>'
            '<option value="12">Ziraat</option>'
            '<option value="13">Garanti</option>'
            '<option value="14">Akbank</option>'
            '<option value="15">Transfers with specific bank</option>'
            '<option value="16">Burgan Bank (K.S.C) (Burgan)</option>'
            '<option value="17">QNB</option>'
            '<option value="18">alBaraka</option>'
            '<option value="19">Fibabanka</option>'
            '<option value="20">Papara</option>'
            '<option value="21">İŞBANK</option>'
            '<option value="22">HalkBank</option>'
        )
        cls.failed_response = (
            f'<option>Payment methods for {cls.currency_try.code}'
            f'does not exist.</option>'
        )
        cls.successful_empty_response_path = (
            'converter/tests/test_data/fail_with_success_true.json'
        )
        cls.from_payment_methods_path = (
            'converter/tests/test_data/SELL_10_records_RUB_mixed.json'
        )
        cls.to_payment_methods_path = (
            'converter/tests/test_data/BUY_10_records_TRY_mixed.json')
        cls.fail_response_path = (
            'converter/tests/test_data/fail_method_unavailable.json')

        with open(cls.fail_response_path, 'r') as file:
            cls.fail_response = file.read()
        with open(cls.successful_empty_response_path, 'r') as file:
            cls.successful_empty_response = file.read()
        with open(cls.from_payment_methods_path, 'r') as file:
            cls.from_json_response = file.read()
        with open(cls.to_payment_methods_path, 'r') as file:
            cls.to_json_response = file.read()

    def test_get_payment_methods_as_select_options(self):
        """Select options HTML for passed currency returned."""
        with patch(
                'converter.views.get_p2p_offers_data') as get_p2p_offers_data:
            get_p2p_offers_data.return_value = self.from_json_response

            response_rub = self.guest_client.get(
                f'/payment_methods/?from_currency={self.currency_rub.pk}')
        with patch(
                'converter.views.get_p2p_offers_data') as get_p2p_offers_data:
            get_p2p_offers_data.return_value = self.to_json_response

            response_try = self.guest_client.get(
                f'/payment_methods/?from_currency={self.currency_try.pk}')

        self.assertEqual(response_rub.status_code, HTTPStatus.OK)
        self.assertEqual(response_rub.content.decode(
            'utf-8'), self.test_response_rub)
        self.assertEqual(response_try.status_code, HTTPStatus.OK)
        self.assertEqual(response_try.content.decode(
            'utf-8'), self.test_response_try)

    def test_get_payment_methods_empty_response(self):
        """Return error message in select option field."""
        with patch(
                'converter.views.get_p2p_offers_data') as get_p2p_offers_data:
            get_p2p_offers_data.return_value = self.successful_empty_response
            response = self.guest_client.get(
                f'/payment_methods/?from_currency={self.currency_rub.pk}')
            self.assertEqual(
                response.content.decode('utf-8'),
                self.payment_method_not_found)

    def test_get_payment_methods_empty_request(self):
        """Return error message in select option field.

        If there is no currency parameters in request context.
        """
        with patch(
                'converter.views.get_p2p_offers_data') as get_p2p_offers_data:
            get_p2p_offers_data.return_value = self.successful_empty_response
            response = self.guest_client.get('/payment_methods/')
            self.assertEqual(
                response.content.decode('utf-8'),
                self.empty_request_response)


class ConverterViewsContextTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
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
        cls.from_payment_methods_path = (
            'converter/tests/test_data/SELL_10_records_RUB_mixed.json')
        cls.to_payment_methods_path = (
            'converter/tests/test_data/BUY_10_records_TRY_mixed.json')

        with open(cls.from_payment_methods_path, 'r') as file:
            cls.from_json_response = file.read()
        with open(cls.to_payment_methods_path, 'r') as file:
            cls.to_json_response = file.read()

        cls.side_effect = [cls.from_json_response,
                           cls.to_json_response,
                           cls.to_json_response, ]

        cls.from_amount = 2000
        cls.conversion_rate = 59.79/18.35
        cls.to_amount = cls.from_amount/cls.conversion_rate
        cls.num_of_offers = 10

        cls.data = {
            'from_currency': cls.currency_rub.pk,
            'to_currency': cls.currency_try.pk,
            'from_payment_methods': cls.payment_method_rub.pk,
            'to_payment_methods': cls.payment_method_try.pk,
            'from_amount': cls.from_amount,
            'is_merchant': True, }

    def test_index_context(self):
        """Main page initial context."""
        response = self.guest_client.get(reverse('converter:index'))
        self.assertIsInstance(response.context['form'], ConverterForm)

    def test_get_offers_context(self):
        """Main page context after successful request."""
        with patch('converter.utils.utils.get_p2p_offers_data'
                   ) as get_p2p_offers_data:
            get_p2p_offers_data.side_effect = self.side_effect
            response = self.guest_client.post(
                reverse('converter:get_offers'), self.data)

            self.assertIsInstance(response.context.get(
                'form'), ConverterForm)
            self.assertEqual(len(response.context.get(
                'from_offers')), self.num_of_offers)
            self.assertEqual(len(response.context.get(
                'to_offers')), self.num_of_offers)
            self.assertEqual(response.context.get(
                'conversion_rate'), self.conversion_rate)
            self.assertEqual(response.context.get(
                'from_amount'), self.from_amount)
            self.assertEqual(response.context.get(
                'to_amount'), self.to_amount)
            self.assertEqual(response.context.get(
                'from_currency'), self.currency_rub)
            self.assertEqual(response.context.get(
                'to_currency'), self.currency_try)
