"""Run the policy lab and write a report the /lab/ page can render.

    manage.py run_policy_lab --trials 400 --seed 7
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core import policy_lab as lab


class Command(BaseCommand):
    help = 'Score editorial policies against simulated review panels. No model calls.'

    def add_arguments(self, parser):
        parser.add_argument('--trials', type=int, default=400, help='Trials per scenario per policy (default 400).')
        parser.add_argument('--seed', type=int, default=7)
        parser.add_argument('--panel', action='append', default=None,
                            help='Panel id to run; repeatable. Default: every shipped panel.')
        parser.add_argument('--out', default=None, help='Report path (default runtime/lab/latest.json).')

    def handle(self, *args, **options):
        trials = options['trials']
        seed = options['seed']
        available = lab.panels()
        wanted = options['panel'] or list(available)
        unknown = [p for p in wanted if p not in available]
        if unknown:
            raise SystemExit(f'unknown panel(s): {", ".join(unknown)}; choose from {", ".join(available)}')

        scenarios = lab.scenarios()
        policies = lab.policies()
        sections = []
        for panel_id in wanted:
            panel = available[panel_id]
            report = lab.run_lab(scenarios, panel, policies, trials=trials, seed=seed)
            section = report.as_dict()
            section['fingerprint'] = lab.fingerprint(report)
            section['recommended'] = {
                risk: (cell.policy_id if (cell := report.best_cell(risk)) else None)
                for risk in lab.RISK_CLASSES
            }
            sections.append(section)

        payload = {
            'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'trials_per_cell': trials,
            'seed': seed,
            'scenarios': len(scenarios),
            'policies': [p.id for p in policies],
            'panels': sections,
        }

        out = Path(options['out']) if options['out'] else Path(settings.GALACTICA['RUNTIME_DIR']) / 'lab' / 'latest.json'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + '\n')
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        (out.parent / f'run-{stamp}.json').write_text(json.dumps(payload, indent=2) + '\n')

        for section in sections:
            self.stdout.write(self.style.MIGRATE_HEADING(
                f"panel {section['panel']} (correlation {section['correlation']})"))
            header = f"{'policy':<16}" + ''.join(f'{risk[:6]:>10}' for risk in lab.RISK_CLASSES)
            self.stdout.write(header)
            self.stdout.write('-' * len(header))
            for policy in policies:
                row = f'{policy.id:<16}'
                for risk in lab.RISK_CLASSES:
                    cell = next(c for c in section['cells'] if c['policy'] == policy.id and c['risk_class'] == risk)
                    row += f"{cell['escape_rate'] * 100:>7.2f}% " if cell['trials'] else f"{'-':>10}"
                self.stdout.write(row)
            self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'wrote {out}'))
