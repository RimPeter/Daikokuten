from django.core.management.base import BaseCommand
from ingestion.services import ingest_training_archive


class Command(BaseCommand):
    help = 'Import tennis training data from a Betfair-style archive.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--archive',
            default='data.tar',
            help='Path to the training archive (default: data.tar).',
        )
        parser.add_argument(
            '--max-files',
            type=int,
            default=100,
            help='Maximum number of archive files to inspect.',
        )
        parser.add_argument(
            '--commit',
            action='store_true',
            help='Persist parsed tennis snapshots into the database.',
        )

    def handle(self, *args, **options):
        archive = options['archive']
        max_files = options['max_files']
        commit = options['commit']

        self.stdout.write(f'Inspecting archive: {archive}')
        self.stdout.write(f'Max files: {max_files}')
        self.stdout.write(f'Persistence enabled: {commit}')

        try:
            summary = ingest_training_archive(archive, max_files=max_files, commit=commit)
        except FileNotFoundError as exc:
            self.stderr.write(str(exc))
            return

        self.stdout.write('')
        self.stdout.write('Archive summary:')
        self.stdout.write(f"  total files scanned: {summary['total_files']}")
        self.stdout.write(f"  tennis snapshot files: {summary['tennis_files']}")
        self.stdout.write(f"  tennis records processed: {summary['tennis_snapshots']}")
        self.stdout.write('  top market types:')
        for market_type, count in summary['market_type_counts']:
            self.stdout.write(f'    {market_type}: {count}')
        self.stdout.write('  top event ids:')
        for event_id, count in summary['event_ids']:
            self.stdout.write(f'    {event_id}: {count}')

        self.stdout.write('  sample tennis markets:')
        for sample in summary['sample_markets']:
            self.stdout.write(f"    eventId={sample['eventId']} marketId={sample['marketId']} marketType={sample['marketType']} marketTime={sample['marketTime']}")

        if commit:
            self.stdout.write('')
            self.stdout.write('Persistence summary:')
            self.stdout.write(f"  created snapshots: {summary['created_snapshots']}")

        self.stdout.write('')
        self.stdout.write('Import completed.')
