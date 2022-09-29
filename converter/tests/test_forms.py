from django.core.exceptions import ValidationError
from django.test import Client, TestCase

from ..forms import ConverterForm
from ..models import Currency, PaymentMethod


class ConverterFormTest(TestCase):
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

        cls.from_amount = 2000
        cls.to_amount = 2000
        cls.negative_from_amount = -2000
        cls.is_merchant = True

    def test_form_validation(self):
        """Form validated fields correctly."""
        valid_data = {
            'from_currency': self.currency_rub.pk,
            'to_currency': self.currency_try.pk,
            'from_payment_methods': self.payment_method_rub.pk,
            'to_payment_methods': self.payment_method_try.pk,
            'from_amount': self.from_amount,
            'is_merchant': self.is_merchant,
        }
        form = ConverterForm(data=valid_data)

        self.assertTrue(form.is_valid())

        from_currency = form.cleaned_data.get('from_currency')
        to_currency = form.cleaned_data.get('to_currency')
        from_payment_method = form.cleaned_data.get('from_payment_methods')
        to_payment_method = form.cleaned_data.get('to_payment_methods')
        is_merchant = form.cleaned_data.get('is_merchant')
        from_amount = form.cleaned_data.get('from_amount')
        to_amount = form.cleaned_data.get('to_amount')

        self.assertEqual(from_currency, self.currency_rub)
        self.assertEqual(to_currency, self.currency_try)
        self.assertEqual(from_payment_method, self.payment_method_rub)
        self.assertEqual(to_payment_method, self.payment_method_try)
        self.assertEqual(is_merchant, self.is_merchant)
        self.assertEqual(from_amount, self.from_amount)
        self.assertIsNone(to_amount)

    def test_same_currency_selected_exception(self):
        """Validation Error if same currency selected for buy and sell."""
        same_currency_data = {
            'from_currency': self.currency_rub.pk,
            'to_currency': self.currency_rub.pk,
            'from_payment_methods': self.payment_method_rub.pk,
            'to_payment_methods': self.payment_method_try.pk,
            'from_amount': self.from_amount,
            'is_merchant': self.is_merchant,
        }
        form = ConverterForm(same_currency_data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError, form.clean)

    def test_both_amount_filled_exception(self):
        """Validation Error if both sell and buy amounts filled."""
        both_amount_filled_data = {
            'from_currency': self.currency_rub.pk,
            'to_currency': self.currency_try.pk,
            'from_payment_methods': self.payment_method_rub.pk,
            'to_payment_methods': self.payment_method_try.pk,
            'from_amount': self.from_amount,
            'to_amount': self.to_amount,
            'is_merchant': self.is_merchant,
        }
        form = ConverterForm(both_amount_filled_data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError, form.clean)

    def test_no_amount_filled_exception(self):
        """Validation Error if neither sell or buy amounts filled."""
        no_amount_filled_data = {
            'from_currency': self.currency_rub.pk,
            'to_currency': self.currency_try.pk,
            'from_payment_methods': self.payment_method_rub.pk,
            'to_payment_methods': self.payment_method_try.pk,
            'is_merchant': self.is_merchant,
        }
        form = ConverterForm(no_amount_filled_data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError, form.clean)

    def test_negative_amount_filled_exception(self):
        """Validation Error if amount filled with negative number."""
        negative_amount_filled_data = {
            'from_currency': self.currency_rub.pk,
            'to_currency': self.currency_try.pk,
            'from_payment_methods': self.payment_method_rub.pk,
            'to_payment_methods': self.payment_method_try.pk,
            'from_amount': self.negative_from_amount,
            'is_merchant': self.is_merchant,
        }
        form = ConverterForm(negative_amount_filled_data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError, form.clean)
