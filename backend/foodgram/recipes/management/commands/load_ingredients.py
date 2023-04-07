import argparse
import json

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = ('Loads ingredients list from .json file.'
            '"name" and "measurement_unit" keys are required.')

    def add_arguments(self, parser):
        parser.add_argument(
            'path_to_data_file',
            nargs='?',
            type=argparse.FileType('r', encoding='UTF-8'),
            default='../../data/ingredients.json',
            help='Path to .json file with data, if empty default will be '
                 'used: ../../data/ingredients.json')

    def handle(self, *args, **options):
        self.stdout.write(
            'Trying to load ingredients list from '
            f'{options["path_to_data_file"].name}'
        )
        with options['path_to_data_file'] as source:
            try:
                data = json.load(source)
                add_counter = 0
                for ingredient in data:
                    if not Ingredient.objects.filter(
                            name=ingredient['name']).exists():
                        Ingredient(
                            name=ingredient['name'],
                            measurement_unit=ingredient[
                                'measurement_unit']).save()
                        add_counter += 1
            except json.decoder.JSONDecodeError as error:
                raise CommandError(f'failed to load json file: {error}')
            except KeyError:
                raise CommandError('wrong data in file')
            except Exception as error:
                raise CommandError(
                    f'something went wrong {type(error)}: {error}'
                )
        self.stdout.write(self.style.SUCCESS(
            f'Successfully added {add_counter} new inrgedients'))
