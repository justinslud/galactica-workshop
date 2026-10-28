import os
import signal
import socket
import time

from django.core.management.base import BaseCommand

from core import jobs


class Command(BaseCommand):
    help = 'Run background workshop jobs. Start it alongside the web app: python manage.py run_worker'

    def add_arguments(self, parser):
        parser.add_argument('--poll', type=float, default=2.0, help='Seconds to wait when the queue is empty.')
        parser.add_argument('--once', action='store_true', help='Run at most one job, then exit.')

    def handle(self, *args, **options):
        worker_id = f'{socket.gethostname()}:{os.getpid()}'
        stop = {'requested': False}

        def request_stop(signum, frame):
            raise KeyboardInterrupt

        signal.signal(signal.SIGTERM, request_stop)
        self.stdout.write(f'worker {worker_id} started; polling every {options["poll"]}s (Ctrl-C to stop)')
        try:
            while True:
                recovered = jobs.recover_stale()
                if recovered:
                    self.stdout.write(f'marked {recovered} stale running job(s) as interrupted')
                job = jobs.run_one(worker_id)
                if job is not None:
                    job.refresh_from_db()
                    self.stdout.write(f'job {str(job.pk)[:8]} {job.kind}: {job.status} {job.error[:120]}')
                    if options['once']:
                        break
                    continue
                if options['once']:
                    break
                time.sleep(options['poll'])
        except KeyboardInterrupt:
            self.stdout.write('worker stopped; any running job was marked interrupted')
