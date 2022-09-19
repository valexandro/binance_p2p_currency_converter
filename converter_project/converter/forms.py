"""Currency converter forms."""
import logging

from django import forms
from dynamic_forms import DynamicField, DynamicFormMixin

from .models import Currency, PaymentMethod

logger = logging.getLogger(__name__)


class ConverterForm(DynamicFormMixin, forms.Form):
    """Currency converter form."""

    ERROR_MESSAGE = (
        'No payment methods for selected currency. '
        'Please select another currency.')

    from_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all()
    )
    to_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all()
    )
    from_payment_methods = DynamicField(
        forms.ModelChoiceField,
        queryset=lambda form: PaymentMethod.objects.filter(
            currency=form['from_currency'].value()),
        initial=lambda form: PaymentMethod.objects.filter(
            currency=form['from_currency'].value()).first(),
        error_messages={
            'invalid_choice': ERROR_MESSAGE,
        }
    )
    to_payment_methods = DynamicField(
        forms.ModelChoiceField,
        queryset=lambda form: PaymentMethod.objects.filter(
            currency=form['to_currency'].value()),
        initial=lambda form: PaymentMethod.objects.filter(
            currency=form['to_currency'].value()).first(),
        error_messages={
            'invalid_choice': ERROR_MESSAGE,
        }
    )
    from_amount = forms.FloatField(required=False)
    to_amount = forms.FloatField(required=False)

    is_merchant = forms.BooleanField(required=False, initial=True)
