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
    # if form.is_valid():
    #     context['POST'] = request.POST
    return render(request, template, context)


def get_payment_methods(request) -> HttpResponse:
    """Return payment method options for requested currency as HTML select options.

    Implemented by DynamicField in ConverterForm.
    Call to forms '*payment_methods' field for requested currency,
    will trigger forms method to fetch payment methods for this currency,
    and assign resulting queryset to choicefield queryset, that will be
    returned as HTML.
    """
    form = ConverterForm(request.GET)
    currency_payment_method = {
        'sell_currency': 'sell_payment_methods',
        'buy_currency': 'buy_payment_methods',
    }
    for currency_type, payment_method in currency_payment_method.items():
        if currency_type in request.GET.keys():
            currency = Currency.objects.get(pk=request.GET.get(currency_type))
            # json = PATHS[currency.code]
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
        currency_to_sell = Currency.objects.get(
            pk=request.POST.get('sell_currency'))
        currency_to_buy = Currency.objects.get(
            pk=request.POST.get('buy_currency'))
        payment_method_to_sell = PaymentMethod.objects.get(
            pk=request.POST.get('sell_payment_methods'))
        payment_method_to_buy = PaymentMethod.objects.get(
            pk=request.POST.get('buy_payment_methods'))
        is_merchant = True if request.POST.get('is_merchant') else False
        if request.POST.get('buy_amount'):
            buy_amount = float(request.POST.get('buy_amount'))
            buy_currency_data = get_p2p_offers_data(
                currency_to_buy.code,
                is_merchant,
                payment_method_to_buy.short_name,
                buy_amount,
                trade_type=TradeType.SELL,
                rows=10,
            )
            sell_currency_data_1 = get_p2p_offers_data(
                currency_to_sell.code,
                is_merchant,
                payment_method_to_sell.short_name,
                None,
                trade_type=TradeType.BUY,
                rows=1,
            )
            buy_offers = get_offers_from_json(buy_currency_data)
            sell_offers_1 = get_offers_from_json(sell_currency_data_1)
            best_buy_price = get_best_price(buy_offers)
            usdt_to_sell = buy_amount/best_buy_price
            best_sell_price_1 = get_best_price(sell_offers_1)
            sell_amount = best_sell_price_1 * usdt_to_sell

            sell_currency_data_2 = get_p2p_offers_data(
                currency_to_sell.code,
                is_merchant,
                payment_method_to_sell.short_name,
                sell_amount,
                trade_type=TradeType.BUY,
                rows=10,
            )
            sell_offers_2 = get_offers_from_json(sell_currency_data_2)
            best_sell_price_2 = get_best_price(sell_offers_2)

            context['buy_offers'] = buy_offers
            context['sell_offers'] = sell_offers_2
            context['conversion_rate'] = best_sell_price_2/best_buy_price
            return render(request, template, context)

        else:
            sell_amount = float(request.POST.get('sell_amount'))
            sell_currency_data = get_p2p_offers_data(
                currency_to_sell.code,
                is_merchant,
                payment_method_to_sell.short_name,
                sell_amount,
                trade_type=TradeType.BUY,
                rows=10,
            )
            buy_currency_data_1 = get_p2p_offers_data(
                currency_to_buy.code,
                is_merchant,
                payment_method_to_buy.short_name,
                None,
                trade_type=TradeType.SELL,
                rows=1,
            )
            sell_offers = get_offers_from_json(sell_currency_data)
            buy_offers_1 = get_offers_from_json(buy_currency_data_1)
            best_sell_price = get_best_price(sell_offers)
            usdt_to_buy = sell_amount/best_sell_price
            best_buy_price_1 = get_best_price(buy_offers_1)
            buy_amount = best_buy_price_1 * usdt_to_buy

            buy_currency_data_2 = get_p2p_offers_data(
                currency_to_buy.code,
                is_merchant,
                payment_method_to_buy.short_name,
                buy_amount,
                trade_type=TradeType.SELL,
                rows=10,
            )
            buy_offers_2 = get_offers_from_json(buy_currency_data_2)
            best_buy_price_2 = get_best_price(buy_offers_2)

            context['buy_offers'] = buy_offers_2
            context['sell_offers'] = sell_offers
            context['conversion_rate'] = best_sell_price/best_buy_price_2
            return render(request, template, context)
    else:
        return render(request, template, context)
