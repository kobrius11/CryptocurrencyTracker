from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.ApiContainer)


class ExchangeModelAdmin(admin.ModelAdmin):
    list_display = ("exchange", )
    prepopulated_fields = {"slug": ("exchange", ), }
admin.site.register(models.ExchangeModel, ExchangeModelAdmin)