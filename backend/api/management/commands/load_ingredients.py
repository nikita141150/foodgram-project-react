import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from api.models import Ingredient

DIR = os.path.join(settings.BASE_DIR, 'data')
FILE_NAME = 'ingredients.json'


class Command(BaseCommand):
    help = 'Загрузка ингредиентов'

    def add_arguments(self, parser):
        parser.add_argument('file', default=FILE_NAME, nargs='?', type=str)

    def handle(self, *args, **options):
        file_path = os.path.join(DIR, options['file'])
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data_len = len(data)
                for n, ingredient in enumerate(data):
                    try:
                        Ingredient.objects.get_or_create(
                            name=ingredient['name'],
                            measurement_unit=ingredient['measurement_unit'])
                    except IntegrityError:
                        print('Ошибка добавления ингредиента')
                    percent_done = 100 * (n + 1) / data_len
                    print(f'  {percent_done:.1f}%', end='\r')
        except FileNotFoundError:
            raise CommandError(f'Отсутствует файл {file_path}')
