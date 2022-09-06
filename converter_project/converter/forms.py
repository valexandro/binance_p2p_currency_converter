"""Currency converter forms."""
import logging

from django import forms
from django.db.models.query import QuerySet
from dynamic_forms import DynamicField, DynamicFormMixin

from .models import Currency, PaymentMethod

logger = logging.getLogger(__name__)


class ConverterForm(DynamicFormMixin, forms.Form):
    """Currency converter form."""

    ERROR_MESSAGE = (
        'No payment methods for selected currency. '
        'Please select another currency.')

    def get_from_payment_methods(form: 'ConverterForm'
                                 ) -> QuerySet[PaymentMethod]:
        """Get queryset of payment methods for selected currency.

        Will be used as callable with form argument by DynamicField field,
        as queryset source.
        """
        from_currency = form['from_currency'].value()
        logger.debug(
            'requested "FROM" payment methods in form')
        return PaymentMethod.objects.filter(currency=from_currency)

    def get_to_payment_methods(form: 'ConverterForm'
                               ) -> QuerySet[PaymentMethod]:
        """Get queryset of payment methods for selected currency.

        Will be used as callable with form argument by DynamicField field,
        as queryset source.
        """
        to_currency = form['to_currency'].value()
        logger.debug(
            'requested "TO" payment methods in form')
        return PaymentMethod.objects.filter(currency=to_currency)

    def initial_from_payment_method(form: 'ConverterForm'
                                    ) -> PaymentMethod:
        """Get first payment method for selected currency.

        Will be used as callable with form argument by DynamicField field,
        as initial field value source.
        """
        from_currency = form['from_currency'].value()
        return PaymentMethod.objects.filter(currency=from_currency).first()

    def initial_to_payment_method(form: 'ConverterForm'
                                  ) -> PaymentMethod:
        """Get first payment method for selected currency.

        Will be used as callable with form argument by DynamicField field,
        as initial field value source.
        """
        to_currency = form['to_currency'].value()
        return PaymentMethod.objects.filter(currency=to_currency).first()

    from_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all()
    )
    to_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all()
    )
    from_payment_methods = DynamicField(
        forms.ModelChoiceField,
        queryset=get_from_payment_methods,
        initial=initial_from_payment_method,
        error_messages={
            'invalid_choice': ERROR_MESSAGE,
        }
    )
    to_payment_methods = DynamicField(
        forms.ModelChoiceField,
        queryset=get_to_payment_methods,
        initial=initial_to_payment_method,
        error_messages={
            'invalid_choice': ERROR_MESSAGE,
        }
    )
    from_amount = forms.FloatField(required=False)
    to_amount = forms.FloatField(required=False)

    is_merchant = forms.BooleanField(required=False, initial=True)
