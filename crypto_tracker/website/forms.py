from django import forms
from django.utils.translation import gettext_lazy as _

from . import models
import ccxt

# news search form
class NewsSearchBar(forms.Form):
    search = forms.CharField(max_length=250)


# class ChartForm(forms.ModelForm):
# #     # tradingview_button = forms.BooleanField(required=False)
# #     exchange= forms.ChoiceField(label=_('Exchange'), choices=((exchange, exchange) for exchange in models.ExchangeModel.objects.all()))
#         class Meta:
# #         model = models.ExchangeModel
# #         fields = ['exchange']
#             widgets = {
#                      }
    

class ApiContainerCreateForm(forms.ModelForm):

    secret_key_text = forms.CharField(label=_('secret key'), widget=forms.PasswordInput())
    class Meta:
        model = models.ApiContainer
        fields = ['exchange', 'name', 'apikey', 'secret_key_text', 'user']
        widgets = {
            'user': forms.HiddenInput(),
        }