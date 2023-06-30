from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


# class NewsArticle(models.Model):
#     title = models.CharField(_("title"), max_length=250)
#     description = models.TextField(_("description"), null=True, blank=True)
#     link = models.
    

#     class Meta:
#         verbose_name = _("newsarticle")
#         verbose_name_plural = _("newsarticles")

#     def __str__(self):
#         return self.name

#     def get_absolute_url(self):
#         return reverse("newsarticle_detail", kwargs={"pk": self.pk})
