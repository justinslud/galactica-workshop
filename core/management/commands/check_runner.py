from django.core.management.base import BaseCommand

from core import configs
from core.runners.opencode import OpenCodeRunner


class Command(BaseCommand):
    help = 'Report whether the OpenCode CLI is available and how many models its catalog lists. Makes no model calls.'

    def handle(self, *args, **options):
        ok, message = OpenCodeRunner().available()
        self.stdout.write(f'OpenCode CLI: {"found" if ok else message}')
        models, error = configs.discover_models(force=True)
        free = [m['id'] for m in models if m['free']]
        self.stdout.write(f'Catalog models: {len(models)} (free by catalog cost: {len(free)})')
        if error:
            self.stdout.write(f'Discovery note: {error}')
        for model_id in free[:12]:
            self.stdout.write(f'  free: {model_id}')
