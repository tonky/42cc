import re
from django.core.management.base import NoArgsCommand
from settings import INSTALLED_APPS
from django.db.models.base import ModelBase


def objects_count(models):
    """ using function here so i could test this on the test db, since
    "manage.py" command runs on the live db
    """

    return [(m.__name__, m.objects.count()) for m in models]


class Command(NoArgsCommand):
    args = 'none'
    help = 'Prints all the models in project with their instances count in db'

    def handle(self, *args, **options):
        models_modules = []
        project_models = []

        # filter apps, that are imported from site-packages
        for installed_app in INSTALLED_APPS:
            module = __import__(installed_app)

            if re.search("site-packages", module.__file__):
                continue

            # filter apps that don't have models
            if not "models" in module.__dict__:
                continue

            if not "models" in module.models.__dict__:
                continue

            # filter models that don't provide "get_apps" functions
            if not "get_apps" in module.models.models.__dict__:
                continue

            # get list of models for current 'models' module
            models = module.models.models.get_apps()

            # filter out models from python install
            for model in models:
                if re.search("python", model.__file__):
                    continue

                models_modules.append(model)

        # get only models classes, that are based on ModelBase
        for module in models_modules:
            for prop in module.__dict__:
                if type(module.__dict__[prop]) == ModelBase:
                    project_models.append(module.__dict__[prop])

        counts = objects_count(project_models)

        for name, count in counts:
            print "%s: %d" % (name, count)
