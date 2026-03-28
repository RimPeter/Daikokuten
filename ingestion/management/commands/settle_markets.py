from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Settle markets based on results.'

    def handle(self, *args, **options):
        self.stdout.write('Settling markets...')
