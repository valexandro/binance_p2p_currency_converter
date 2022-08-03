from django.urls import path

from . import views

app_name = 'converter'

urlpatterns = [
    path('', views.index, name='index'),
    path('payment_methods/',
         views.get_payment_methods,
         name='payment_methods'),
]
