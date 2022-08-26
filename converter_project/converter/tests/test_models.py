from django.test import TestCase

from ..models import Currency, PaymentMethod


class ConverterModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.currency_code = 'CUR'
        cls.currency_name = 'Test Currency'
        cls.payment_method_1_id = 'PaymentMethod1'
        cls.payment_method_1_display_name = 'Payment Method 1'
        cls.payment_method_2_id = 'PaymentMethod2'
        cls.currency = Currency.objects.create(
            code=cls.currency_code,
            name=cls.currency_name,
        )
        cls.payment_method_with_display_name = PaymentMethod.objects.create(
            short_name=cls.payment_method_1_id,
            display_name=cls.payment_method_1_display_name,
            currency=cls.currency,
        )
        cls.payment_method_without_display_name = PaymentMethod.objects.create(
            short_name=cls.payment_method_2_id,
            currency=cls.currency,
        )

    def test_models_str_methods(self):
        """__str__ methods is correct."""
        self.assertEqual(self.currency_code, str(self.currency))
        self.assertEqual(self.payment_method_1_display_name,
                         str(self.payment_method_with_display_name))
        self.assertEqual(self.payment_method_2_id,
                         str(self.payment_method_without_display_name))
