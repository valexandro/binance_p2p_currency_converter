import logging

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .exceptions import BinanceApiError, OffersNotFoundError
from .forms import ConverterForm
from .models import Currency, PaymentMethod
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
            json = get_p2p_offers_data(
                fiat_code=currency.code, is_merchant=True, rows=10)
            try:
                get_payment_methods_from_json(json)
            except OffersNotFoundError:
                logger.info(f'no payment methods found for {currency.code}')
                return HttpResponse(error_message.format(currency.code))
            except BinanceApiError as e:
                logger.error(e)
                return HttpResponse('<option>Request Failed</option>')
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
    if (not request.POST.get('to_amount')
            and not request.POST.get('from_amount')):
        messages.error(request, 'Please fill one of amount fields!')
        return render(request, template, context)

    if request.POST.get('from_currency') == request.POST.get('to_currency'):
        messages.error(request, 'From and to currencies cannot be the same!')
        return render(request, template, context)

    to_amount_filled = True if request.POST.get('to_amount') else False

    filled_amount: float

    if to_amount_filled:
        filled_amount = float(request.POST.get('to_amount'))
    else:
        filled_amount = float(request.POST.get('from_amount'))

    if filled_amount <= 0:
        messages.error(request, 'Amount should be greater than zero!')
        return render(request, template, context)

    if form.is_valid():
        from_currency = get_object_or_404(
            Currency,
            pk=request.POST.get('from_currency'))
        to_currency = get_object_or_404(
            Currency,
            pk=request.POST.get('to_currency'))
        from_payment_method = get_object_or_404(
            PaymentMethod,
            pk=request.POST.get('from_payment_methods'))
        to_payment_method = get_object_or_404(
            PaymentMethod,
            pk=request.POST.get('to_payment_methods'))
        is_merchant = True if request.POST.get('is_merchant') else False
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
