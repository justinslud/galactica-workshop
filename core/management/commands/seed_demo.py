from django.core.management.base import BaseCommand

from core import seeding


class Command(BaseCommand):
    help = 'Create demonstration articles, sources, presets, test cases and example jobs. Safe to run twice.'

    def handle(self, *args, **options):
        seeding.seed(log=self.stdout.write)
