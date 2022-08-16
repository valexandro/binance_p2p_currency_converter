from django.urls import path

from . import views

app_name = 'converter'

urlpatterns = [
    path('payment_methods/',
         views.get_payment_methods,
         name='payment_methods'),
    path('get_offers/',
         views.get_offers,
         name='get_offers'),
    path('', views.index, name='index'),
]
