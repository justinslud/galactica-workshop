import json
import sys

from django.core.management.base import BaseCommand

from core import search


class Command(BaseCommand):
    help = 'Compare the FTS5 index with SearchDocument and run the FTS integrity check.'

    def handle(self, *args, **options):
        report = search.check_index()
        self.stdout.write(json.dumps(report, indent=2))
        if not report['ok']:
            sys.exit(1)
