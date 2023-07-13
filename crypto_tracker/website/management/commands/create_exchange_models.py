from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from website.models import ExchangeModel
import ccxt


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        created_exchanges_count = 0
        try:
            for exchange in ccxt.exchanges:
                model = ExchangeModel.objects.create(
                    exchange=exchange,
                    slug=exchange,
                    )
                
                model.save()
                created_exchanges_count += 1
        except Exception as e:
            raise CommandError(e)
        else:
            self.stdout.write(
                self.style.SUCCESS('%d exchange models created' % created_exchanges_count)
            )