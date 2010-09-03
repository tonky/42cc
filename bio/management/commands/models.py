import re
from django.core.management.base import NoArgsCommand
from settings import INSTALLED_APPS
from django.db.models.base import ModelBase


class Command(NoArgsCommand):
    args = 'none'
    help = 'Prints all the models in project with their instances count in db'

    def handle(self, *args, **options):
        project_apps = []
        project_models = []

        for installed_app in INSTALLED_APPS:
            module = __import__(installed_app)

            if re.search("site-packages", module.__file__):
                continue

            if not "models" in module.models.__dict__:
                continue

            if not "get_apps" in module.models.models.__dict__:
                continue

            module_apps = module.models.models.get_apps()

            for app in module_apps:
                if re.search("site-packages", app.__file__):
                    continue

                project_apps.append(app)


        for app in project_apps:
            for prop in app.__dict__:
                if type(app.__dict__[prop]) == ModelBase:
                    project_models.append(app.__dict__[prop])

        for m in project_models:
            print "%s: %d" % (m.__name__, m.objects.count())
