from django.core.management.base import BaseCommand
from modelling.tasks import generate_predictions


class Command(BaseCommand):
    help = 'Generate and persist tennis market predictions using the modelling pipeline.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            default='betlab_tennis',
            help='Model run name.',
        )
        parser.add_argument(
            '--model-version',
            dest='model_version',
            default='',
            help='Model version identifier.',
        )
        parser.add_argument(
            '--note',
            default='',
            help='Optional note for the model run.',
        )

    def handle(self, *args, **options):
        name = options['name']
        version = options['model_version']
        note = options['note']

        self.stdout.write(f'Generating predictions for model {name} version {version}')
        result = generate_predictions(name, version, note)

        self.stdout.write('Prediction generation completed.')
        self.stdout.write(f"Model run id: {result.get('model_run_id')}")
        self.stdout.write(f"Created predictions: {result.get('created_predictions')}")
