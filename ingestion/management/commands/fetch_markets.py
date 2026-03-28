from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Fetch markets from the ingestion source.'

    def handle(self, *args, **options):
        self.stdout.write('Fetching markets...')
