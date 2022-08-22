from django.http import HttpResponse
from django.shortcuts import render

from .utils.utils import get_best_price

from .forms import ConverterForm
from .models import Currency, PaymentMethod, TradeType
from .utils.binance_api import get_p2p_offers_data
from .utils.json_parser import get_offers_from_json, parse_payment_methods


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

    Implemented by DynamicField in ConverterForm.
    Call to forms '*payment_methods' field for requested currency,
    will trigger forms method to fetch payment methods for this currency,
    and assign resulting queryset to choicefield queryset, that will be
    returned as HTML.
    """
    # template = 'converter/index.html'
    form: ConverterForm = ConverterForm(request.GET)
    currency_payment_method_field_names = {
        'from_currency': 'from_payment_methods',
        'to_currency': 'to_payment_methods',
    }
    for currency_type, payment_method in currency_payment_method_field_names.items():

        if currency_type in request.GET.keys():
            currency = Currency.objects.get(pk=request.GET.get(currency_type))
            json = get_p2p_offers_data(currency.code)
            payment_methods = parse_payment_methods(json)
            if not payment_methods:
                return HttpResponse(
                    f'<option>Payment methods for {currency.code} not exists.</option>')
            return HttpResponse(form[payment_method])


def get_offers(request):
    template = 'converter/index.html'
    form = ConverterForm(
        request.POST or None)
    context = {
        'form': form,
    }
    if form.is_valid():
        context['POST'] = request.POST
        from_currency = Currency.objects.get(
            pk=request.POST.get('from_currency'))
        to_currency = Currency.objects.get(
            pk=request.POST.get('to_currency'))
        from_payment_method = PaymentMethod.objects.get(
            pk=request.POST.get('from_payment_methods'))
        to_payment_method = PaymentMethod.objects.get(
            pk=request.POST.get('to_payment_methods'))
        is_merchant = True if request.POST.get('is_merchant') else False
        if request.POST.get('to_amount'):
            to_amount = float(request.POST.get('to_amount'))
            to_currency_data = get_p2p_offers_data(
                to_currency.code,
                is_merchant,
                to_payment_method.short_name,
                to_amount,
                trade_type=TradeType.SELL,
                rows=10,
            )
            from_currency_data_1 = get_p2p_offers_data(
                from_currency.code,
                is_merchant,
                from_payment_method.short_name,
                None,
                trade_type=TradeType.BUY,
                rows=1,
            )
            to_offers = get_offers_from_json(to_currency_data)
            from_offers_1 = get_offers_from_json(from_currency_data_1)
            best_to_price = get_best_price(to_offers)
            usdt_to_sell = to_amount/best_to_price
            best_from_price_1 = get_best_price(from_offers_1)
            from_amount = best_from_price_1 * usdt_to_sell

            from_currency_data_2 = get_p2p_offers_data(
                from_currency.code,
                is_merchant,
                from_payment_method.short_name,
                from_amount,
                trade_type=TradeType.BUY,
                rows=10,
            )
            from_offers_2 = get_offers_from_json(from_currency_data_2)
            best_from_price_2 = get_best_price(from_offers_2)

            offers = zip(from_offers_2, to_offers)
            context['offers'] = offers
            context['conversion_rate'] = best_from_price_2/best_to_price
            context['to_amount'] = to_amount
            context['from_amount'] = from_amount
            context['to_currency'] = to_currency
            context['from_currency'] = from_currency
            return render(request, template, context)

        else:
            from_amount = float(request.POST.get('from_amount'))
            from_currency_data = get_p2p_offers_data(
                from_currency.code,
                is_merchant,
                from_payment_method.short_name,
                from_amount,
                trade_type=TradeType.BUY,
                rows=10,
            )
            to_currency_data_1 = get_p2p_offers_data(
                to_currency.code,
                is_merchant,
                to_payment_method.short_name,
                None,
                trade_type=TradeType.SELL,
                rows=1,
            )
            from_offers = get_offers_from_json(from_currency_data)
            to_offers_1 = get_offers_from_json(to_currency_data_1)
            best_from_price = get_best_price(from_offers)
            usdt_to_buy = from_amount/best_from_price
            best_to_price_1 = get_best_price(to_offers_1)
            to_amount = best_to_price_1 * usdt_to_buy

            to_currency_data_2 = get_p2p_offers_data(
                to_currency.code,
                is_merchant,
                to_payment_method.short_name,
                to_amount,
                trade_type=TradeType.SELL,
                rows=10,
            )
            to_offers_2 = get_offers_from_json(to_currency_data_2)
            best_to_price_2 = get_best_price(to_offers_2)
            offers = zip(from_offers, to_offers_2)
            context['offers'] = offers
            context['conversion_rate'] = best_from_price/best_to_price_2
            context['to_amount'] = to_amount
            context['from_amount'] = from_amount
            context['to_currency'] = to_currency
            context['from_currency'] = from_currency
            return render(request, template, context)
    else:
        return render(request, template, context)
