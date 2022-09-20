import logging

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .exceptions import (ApiUnavailableError, BinanceApiError,
                         OffersNotFoundError)
from .forms import ConverterForm
from .models import Currency
from .utils.binance_api import get_p2p_offers_data
from .utils.json_parser import get_payment_methods_from_json
from .utils.utils import get_best_offers_lists, get_best_price

logger = logging.getLogger(__name__)


def index(request) -> HttpResponse:
    """Handle requests to main converter page."""
    template = 'converter/index.html'
    form = ConverterForm()
    context = {
        'form': form,
    }
    return render(request, template, context)


def get_payment_methods(request) -> HttpResponse:
    """Return payment method options for requested currency as HTML select options.

    Implemented by DynamicField in ConverterForm + HTMX.
    Call to forms '*payment_methods' field for requested currency,
    will trigger forms method to fetch payment methods for this currency,
    and assign resulting queryset to choicefield queryset, that will be
    returned as HTML.
    """
    form: ConverterForm = ConverterForm(request.GET)
    currency_payment_method_field = {
        'from_currency': 'from_payment_methods',
        'to_currency': 'to_payment_methods',
    }
    error_message = (
        '<option>Payment methods for {0} does not exist.</option>')
    for currency_type, payment_method in currency_payment_method_field.items():
        if currency_type in request.GET.keys():
            currency = get_object_or_404(
                Currency, pk=request.GET.get(currency_type))
            logger.info(f'requested payment methods for {currency.code}')
            try:
                json = get_p2p_offers_data(
                    fiat_code=currency.code, is_merchant=True, rows=10)
            except ApiUnavailableError as e:
                return HttpResponse(f'<option>{e}</option>')
            try:
                get_payment_methods_from_json(json)
            except OffersNotFoundError:
                logger.info(f'no payment methods found for {currency.code}')
                return HttpResponse(error_message.format(currency.code))
            except BinanceApiError as e:
                logger.error(e)
                return HttpResponse(f'<option>{e}</option>')
            return HttpResponse(form[payment_method])
    logger.error('HTMX created empty request.')
    return HttpResponse('<option value="">---------</option>')


def get_offers(request):
    """Handle currency conversion requests."""
    template = 'converter/index.html'
    form = ConverterForm(
        request.POST or None)
    context = {
        'form': form,
    }

    if form.is_valid():
        to_amount_filled = True if form.cleaned_data.get(
            'to_amount') else False
        from_currency = form.cleaned_data.get('from_currency')
        to_currency = form.cleaned_data.get('to_currency')
        from_payment_method = form.cleaned_data.get('from_payment_methods')
        to_payment_method = form.cleaned_data.get('to_payment_methods')
        is_merchant = form.cleaned_data.get('is_merchant')
        filled_amount = (form.cleaned_data.get('to_amount') if to_amount_filled
                         else form.cleaned_data.get('from_amount'))
        try:
            if to_amount_filled:
                to_amount = filled_amount
                logger.info(
                    f'requested conversion '
                    f'{from_currency.code}'
                    f'[{from_payment_method.display_name}] -> '
                    f'({to_amount}){to_currency.code}'
                    f'[{to_payment_method.display_name}]')

                from_offers, to_offers = get_best_offers_lists(
                    to_currency, from_currency, to_payment_method,
                    from_payment_method, is_merchant, to_amount,
                    to_amount_filled)

                best_from_price = get_best_price(from_offers)
                best_to_price = get_best_price(to_offers)
                conversion_rate = best_from_price/best_to_price
                from_amount = to_amount*conversion_rate
            else:
                from_amount = filled_amount
                logger.info(
                    f'requested conversion '
                    f'({from_amount}){from_currency.code}'
                    f'[{from_payment_method.display_name}] -> '
                    f'{to_currency.code}[{to_payment_method.display_name}]')

                to_offers, from_offers = get_best_offers_lists(
                    from_currency, to_currency, from_payment_method,
                    to_payment_method, is_merchant, from_amount,
                    to_amount_filled)

                best_from_price = get_best_price(from_offers)
                best_to_price = get_best_price(to_offers)
                conversion_rate = best_from_price/best_to_price
                to_amount = from_amount/conversion_rate
        except Exception as e:
            messages.error(request, str(e))
            return render(request, template, context)

        context = {
            'form': form,
            'offers': zip(from_offers, to_offers),
            'from_offers': from_offers,
            'to_offers': to_offers,
            'conversion_rate': conversion_rate,
            'to_amount': to_amount,
            'from_amount': from_amount,
            'to_currency': to_currency,
            'from_currency': from_currency,
        }
        messages.success(request,
                         f'Successfully converted {from_amount:.3f} '
                         f'{from_currency} to {to_amount} {to_currency}')

        logger.info('offers rendered on index page.')
        return render(request, template, context)
    else:
        messages.error(request, form.errors)
        logger.error(form.errors)
        return render(request, template, context)
