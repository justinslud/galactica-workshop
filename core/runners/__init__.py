"""Runner boundary. A runner turns a Task into a validated JSON result. Nothing else in the app talks to a model."""
from dataclasses import dataclass, field


class RunnerError(Exception):
    """The runner could not produce a usable result. Message is shown to users; never includes secrets."""


class JobCancelled(Exception):
    pass


class BudgetExceeded(RunnerError):
    pass


@dataclass
class Task:
    kind: str            # 'draft' | 'edit' | 'review'
    model: str
    payload: dict = field(default_factory=dict)
    role: str = ''
    label: str = ''
    profile: str = ''


class ModelRunner:
    name = 'base'
    label = 'base'

    def call(self, ctx, task):
        """Return the validated result dict for task.kind. Raise RunnerError on failure."""
        raise NotImplementedError


def get_runner(name):
    if name == 'simulated':
        from .simulated import SimulatedRunner
        return SimulatedRunner()
    if name == 'opencode':
        from .opencode import OpenCodeRunner
        return OpenCodeRunner()
    raise RunnerError(f'Unknown runner: {name}')
