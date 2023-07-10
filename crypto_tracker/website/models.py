from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ccxt import exchanges


class ApiContainer(models.Model):
    exchange = models.CharField(_("exhcange"), choices=((exchange, exchange) for exchange in exchanges))
    name = models.CharField(_("name"), max_length=250)
    description = models.TextField(_("description"))
    apikey = models.CharField(_("apikey"), max_length=250)
    secret_key = models.CharField(_("secret key"), max_length=250)
    user = models.ForeignKey(get_user_model(), verbose_name=_("user"), on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = _("Api container")
        verbose_name_plural = _("Api containers")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("apicontainer_detail", kwargs={"pk": self.pk})