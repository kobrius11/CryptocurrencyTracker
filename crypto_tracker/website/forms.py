from django import forms
from . import models

# news search form
class NewsSearchBar(forms.Form):
    search = forms.CharField(max_length=250)
