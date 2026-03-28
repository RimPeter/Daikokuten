from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Fetch market snapshots from the ingestion source.'

    def handle(self, *args, **options):
        self.stdout.write('Fetching snapshots...')
