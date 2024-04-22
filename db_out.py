from django.core.management.base import BaseCommand
from django.apps import apps
import json


class Command(BaseCommand):
    help = "Dump data with UTF-8 encoding"

    def handle(self, *args, **options):
        models = apps.get_models()
        data = []
        for model in models:
            model_data = list(model.objects.all().values())
            data.append({model.__name__: model_data})

        with open("db_dump.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
