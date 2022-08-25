import json

from django.apps import apps
from django.core.management.base import BaseCommand

from foodgram import settings


def application_existence_check(app_name):
    """Проверка существования указанного приложения"""
    for app_class in apps.get_app_configs():
        if app_name == app_class.name:
            return app_class
    raise LookupError('Указанное приложение не найдено.')


def model_existence_check(app_class, model_name):
    """Проверка существования указанной модели в приложении"""
    for model_class in app_class.get_models():
        if model_name == model_class.__name__:
            return model_class
    raise LookupError('Указанная модель в приложении не найдена')


def read_json(file):
    with open(file, "r") as read_file:
        data = json.load(read_file)
        return data


def create_objects(model, data):
    try:
        i = model.objects.latest('pk').pk
    except model.DoesNotExist:
        i = 0
    objs = []
    for valums in data:
        i += 1
        objs.append(model(id=i, **valums))
        if len(objs) == 99:
            crt = model.objects.bulk_create(objs, len(data))
            objs = []
    return model.objects.bulk_create(objs, len(data))


class Command(BaseCommand):
    help = 'Загрузка данных в модель из json-файлов'

    def add_arguments(self, parser):
        parser.add_argument('app', type=str, help='Приложение')
        parser.add_argument('model', type=str, help='Модель')
        parser.add_argument('filename', type=str, help='Файл')

    def handle(self, *args, **options):
        """Обработчик команды"""
        app_class = application_existence_check(options['app'])
        model_class = model_existence_check(app_class, options['model'])
        file_path = (
            settings.TEST_DATA_DIR
            + (options['filename'] or (options['model'] + '.json'))
        )

        data = read_json(file_path)
        create_objects(model_class, data)
