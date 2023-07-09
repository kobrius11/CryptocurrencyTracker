from django import forms
from django.utils.translation import gettext_lazy as _

from . import models
import ccxt

# news search form
class NewsSearchBar(forms.Form):
    search = forms.CharField(max_length=250)


class ChartForm(forms.Form):
    tradingview_button = forms.BooleanField(required=False)
    exchange = forms.ChoiceField(label=_('exchange choice'), choices=((ccxt.exchanges[i], ccxt.exchanges[i]) for i in range(len(ccxt.exchanges))), required=False)


class CreateModelForm(forms.ModelForm):

    class Meta:
        model = None
        fields = []
        widgets = {

        }