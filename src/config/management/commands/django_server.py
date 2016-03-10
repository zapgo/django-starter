from django.core.management import call_command, BaseCommand


class Command(BaseCommand):
    help = "Migrate and deploy!"

    def handle(self, *args, **options):
        # call_command('collectstatic', verbosity=1, interactive=False)
        # call_command('makemigrations', verbosity=1, interactive=False)
        call_command('migrate', verbosity=1, interactive=False)
        call_command('runserver', '0.0.0.0:8000', verbosity=1, interactive=False)
