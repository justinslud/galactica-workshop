import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q


class Article(models.Model):
    PROVENANCE = [
        ('demonstration', 'Demonstration draft (illustrative, not verified)'),
        ('workshop', 'Workshop article'),
        ('agent', 'Agent-produced (pending human decision)'),
        ('simulated', 'SIMULATED output'),
    ]

    slug = models.SlugField(max_length=120, unique=True)
    title = models.CharField(max_length=200)
    opening = models.TextField(blank=True)
    provenance = models.CharField(max_length=20, choices=PROVENANCE, default='workshop')
    published = models.ForeignKey(
        'Revision', null=True, blank=True, on_delete=models.PROTECT, related_name='+'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Revision(models.Model):
    """An immutable snapshot of an article, except while it is the open draft."""

    STATES = [
        ('draft', 'Draft'),
        ('proposed', 'Proposed'),
        ('published', 'Published'),
        ('superseded', 'Superseded'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='revisions')
    number = models.PositiveIntegerField()
    state = models.CharField(max_length=20, choices=STATES, default='draft')
    title = models.CharField(max_length=200)
    opening = models.TextField(blank=True)
    summary = models.CharField(max_length=300, blank=True)
    reverts = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='reverted_by')
    content_hash = models.CharField(max_length=64, blank=True)
    version = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-number']
        constraints = [
            models.UniqueConstraint(fields=['article', 'number'], name='unique_revision_number'),
            models.UniqueConstraint(
                fields=['article'], condition=Q(state='draft'), name='one_open_draft_per_article'
            ),
        ]

    def __str__(self):
        return f'{self.article.slug} r{self.number} ({self.state})'

    @property
    def label(self):
        return f'r{self.number}'


class Block(models.Model):
    KINDS = [
        ('markdown', 'Markdown text'),
        ('image', 'Image'),
        ('table', 'Table'),
        ('timeline', 'Timeline'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    block_id = models.UUIDField(help_text='Stable across revisions; proposals and evidence target this id.')
    revision = models.ForeignKey(Revision, on_delete=models.CASCADE, related_name='blocks')
    position = models.PositiveIntegerField()
    kind = models.CharField(max_length=20, choices=KINDS)
    data = models.JSONField(default=dict)

    class Meta:
        ordering = ['position']
        constraints = [
            models.UniqueConstraint(fields=['revision', 'block_id'], name='unique_block_per_revision'),
        ]


class Source(models.Model):
    CHECK = [
        ('opened', 'Opened and checked by a maintainer'),
        ('metadata', 'Metadata only (not opened)'),
        ('fetched', 'Fetched automatically (not human-verified)'),
        ('unchecked', 'Unchecked'),
    ]
    KINDS = [
        ('paper', 'Paper'),
        ('encyclopedia', 'Encyclopedia / secondary'),
        ('web', 'Web page'),
        ('book', 'Book'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    url = models.URLField(blank=True)
    kind = models.CharField(max_length=20, choices=KINDS, default='other')
    authors = models.CharField(max_length=300, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    published_on = models.CharField(max_length=60, blank=True)
    retrieved_on = models.DateField(null=True, blank=True)
    check_status = models.CharField(max_length=20, choices=CHECK, default='unchecked')
    retrieval_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Claim(models.Model):
    """One factual unit inside a readable block. Stable claim id for the revision and reviewers."""

    STATUS = [
        ('direct', 'Direct support'),
        ('partial', 'Partial support'),
        ('conflicting', 'Conflicting sources'),
        ('absent', 'No citation'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    revision = models.ForeignKey('Revision', on_delete=models.CASCADE, related_name='claims')
    block_id = models.UUIDField()
    position = models.PositiveIntegerField()
    text = models.TextField()
    start = models.PositiveIntegerField(null=True, blank=True)
    end = models.PositiveIntegerField(null=True, blank=True)
    support_status = models.CharField(max_length=16, choices=STATUS, default='absent')
    support_note = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ['position']
        constraints = [
            models.UniqueConstraint(fields=['revision', 'block_id', 'position'], name='unique_claim_position'),
        ]

    def __str__(self):
        return self.text[:80]


class Citation(models.Model):
    """Evidence attached to one block and, when available, one claim in one revision."""

    STANCE = [('supports', 'Supports'), ('conflicts', 'Conflicts'), ('context', 'Context only')]
    STRENGTH = [('direct', 'Direct'), ('partial', 'Partial')]

    revision = models.ForeignKey(Revision, on_delete=models.CASCADE, related_name='citations')
    block_id = models.UUIDField()
    claim = models.ForeignKey(Claim, null=True, blank=True, on_delete=models.SET_NULL, related_name='citations')
    source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name='citations')
    supports = models.TextField(help_text='What this source is cited for.')
    quote = models.TextField(blank=True)
    stance = models.CharField(max_length=12, choices=STANCE, default='supports')
    strength = models.CharField(max_length=12, choices=STRENGTH, default='direct')

    class Meta:
        ordering = ['id']


class Proposal(models.Model):
    STATUS = [
        ('pending', 'Awaiting decision'),
        ('approved', 'Approved, not yet published'),
        ('rejected', 'Rejected'),
        ('revision_requested', 'Revision requested'),
        ('published', 'Published'),
    ]
    ORIGIN = [
        ('human', 'Human editor'),
        ('simulated', 'SIMULATED runner'),
        ('opencode', 'OpenCode runner'),
        ('agent', 'Agent editorial cycle'),
        ('evaluation', 'Evaluation case (never publishable)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='proposals')
    base = models.ForeignKey(Revision, null=True, blank=True, on_delete=models.PROTECT, related_name='proposals_on_base')
    candidate = models.OneToOneField(Revision, on_delete=models.PROTECT, related_name='proposal')
    status = models.CharField(max_length=24, choices=STATUS, default='pending')
    origin = models.CharField(max_length=20, choices=ORIGIN, default='human')
    rationale = models.TextField()
    repeat_of = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='repeats')
    eval_case = models.ForeignKey('EvalCase', null=True, blank=True, on_delete=models.SET_NULL, related_name='proposals')
    result = models.ForeignKey(Revision, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    agent = models.ForeignKey('Agent', null=True, blank=True, on_delete=models.SET_NULL, related_name='proposals')
    origin_job = models.ForeignKey('Job', null=True, blank=True, on_delete=models.SET_NULL, related_name='origin_proposals')
    origin_model = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_note = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Proposal {str(self.id)[:8]} on {self.article.slug}'

    @property
    def is_stale(self):
        return self.base_id != self.article.published_id


class Review(models.Model):
    VERDICTS = [
        ('support', 'Support'),
        ('concern', 'Concern'),
        ('object', 'Object'),
        ('abstain', 'Abstain'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='reviews')
    role = models.CharField(max_length=40)
    verdict = models.CharField(max_length=10, choices=VERDICTS)
    comment = models.TextField(blank=True)
    evidence_notes = models.TextField(blank=True)
    origin = models.CharField(max_length=20, default='simulated')
    declared_model = models.CharField(max_length=120, blank=True, help_text='Declared by the runner. Not verified identity.')
    claim_verdicts = models.JSONField(default=dict, blank=True, help_text='claim id -> verdict/issue/comment.')
    agent = models.ForeignKey('Agent', null=True, blank=True, on_delete=models.SET_NULL, related_name='reviews')
    agent_run = models.ForeignKey('AgentRun', null=True, blank=True, on_delete=models.SET_NULL, related_name='reviews')
    job = models.ForeignKey('Job', null=True, blank=True, on_delete=models.SET_NULL, related_name='reviews')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(fields=['proposal', 'role'], name='one_review_per_role'),
        ]


class Job(models.Model):
    KINDS = [
        ('research_draft', 'Research and draft an article'),
        ('propose_edit', 'Propose an improvement'),
        ('review_proposal', 'Review a proposal'),
        ('run_eval', 'Run editorial test cases'),
        ('agent_cycle', 'Bounded agent editorial cycle'),
    ]
    STATUS = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('interrupted', 'Interrupted'),
    ]
    TERMINAL = ('succeeded', 'failed', 'cancelled', 'interrupted')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=32, choices=KINDS)
    status = models.CharField(max_length=20, choices=STATUS, default='queued')
    runner = models.CharField(max_length=20, default='simulated')
    label = models.CharField(max_length=200, blank=True)
    article = models.ForeignKey(Article, null=True, blank=True, on_delete=models.SET_NULL, related_name='jobs')
    proposal = models.ForeignKey(Proposal, null=True, blank=True, on_delete=models.SET_NULL, related_name='jobs')
    input = models.JSONField(default=dict)
    config_snapshot = models.JSONField(default=dict, help_text='Configuration resolved when the job was queued.')
    output = models.JSONField(default=dict, blank=True)
    usage = models.JSONField(default=dict, blank=True, help_text='Measured usage only. Empty means not measured.')
    error = models.TextField(blank=True)
    cancel_requested = models.BooleanField(default=False)
    retry_of = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='retries')
    model_calls = models.PositiveIntegerField(default=0)
    max_model_calls = models.PositiveIntegerField(default=8)
    timeout_seconds = models.PositiveIntegerField(default=900)
    worker_id = models.CharField(max_length=80, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    heartbeat_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_kind_display()} [{self.status}]'

    @property
    def is_terminal(self):
        return self.status in self.TERMINAL

    @property
    def can_cancel(self):
        return self.status in ('queued', 'running') and not self.cancel_requested

    @property
    def can_retry(self):
        return self.status in ('failed', 'cancelled', 'interrupted')


class JobEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, default='info')
    message = models.TextField()

    class Meta:
        ordering = ['id']


class ConfigVersion(models.Model):
    KINDS = [
        ('instructions', 'Instructions'),
        ('reviewers', 'Reviewer panel'),
        ('runner', 'Runner and model'),
        ('policy', 'Publication policy'),
        ('limits', 'Job limits'),
        ('research', 'Research and source intake'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=20, choices=KINDS)
    family = models.CharField(max_length=80)
    name = models.CharField(max_length=120)
    version = models.PositiveIntegerField(default=1)
    data = models.JSONField(default=dict)
    description = models.TextField(blank=True)
    provisional = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['kind', 'family', '-version']
        constraints = [
            models.UniqueConstraint(fields=['kind', 'family', 'version'], name='unique_config_version'),
            models.UniqueConstraint(fields=['kind'], condition=Q(is_default=True), name='one_default_per_kind'),
        ]

    def __str__(self):
        return f'{self.get_kind_display()}: {self.name} v{self.version}'

    @property
    def proposal_only(self):
        return self.kind == 'policy' and self.family == 'low-risk-shadow-proposal'


class EvalCase(models.Model):
    CATEGORIES = [
        ('supported_correction', 'Supported factual correction'),
        ('irrelevant_citation', 'Claim with an irrelevant citation'),
        ('removed_qualification', 'Removal of an important qualification'),
        ('unreadable_rewrite', 'Accurate but unreadable rewrite'),
        ('conflicting_proposals', 'Conflicting proposals against one revision'),
        ('repeated_rejected', 'Repetition of a rejected proposal'),
    ]
    OUTCOMES = [
        ('supported', 'Supported (no objection, enough support)'),
        ('contested', 'Contested (concerns raised)'),
        ('objected', 'Objected (blocking objection)'),
        ('unknown', 'Unknown (no expectation recorded)'),
    ]
    LABELS = [
        ('human', 'Human-labeled'),
        ('simulated', 'Simulated expectation (not a human label)'),
        ('unknown', 'Unlabeled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=40, choices=CATEGORIES)
    description = models.TextField(blank=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='eval_cases')
    scenario = models.JSONField(default=dict, help_text='Candidate edits applied to the base revision.')
    expected = models.CharField(max_length=20, choices=OUTCOMES, default='unknown')
    label_source = models.CharField(max_length=20, choices=LABELS, default='unknown')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class EvalResult(models.Model):
    id = models.BigAutoField(primary_key=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='eval_results')
    case = models.ForeignKey(EvalCase, on_delete=models.CASCADE, related_name='results')
    candidate_label = models.CharField(max_length=60, default='A')
    proposal = models.ForeignKey(Proposal, null=True, blank=True, on_delete=models.SET_NULL, related_name='eval_results')
    outcome = models.CharField(max_length=20)
    verdicts = models.JSONField(default=dict)
    expected = models.CharField(max_length=20)
    matches = models.BooleanField(null=True, help_text='Null when expectation is unknown.')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']


class AuditEvent(models.Model):
    """Who did what, when, why, and what revision resulted."""

    id = models.BigAutoField(primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='audit_events')
    revision = models.ForeignKey(Revision, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    proposal = models.ForeignKey(Proposal, null=True, blank=True, on_delete=models.SET_NULL, related_name='audit_events')
    job = models.ForeignKey(Job, null=True, blank=True, on_delete=models.SET_NULL, related_name='audit_events')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    agent = models.ForeignKey('Agent', null=True, blank=True, on_delete=models.SET_NULL, related_name='audit_events')
    agent_run = models.ForeignKey('AgentRun', null=True, blank=True, on_delete=models.SET_NULL, related_name='audit_events')
    model = models.CharField(max_length=160, blank=True, help_text='Model declared by the runner for this action.')
    config_versions = models.JSONField(default=dict, blank=True,
                                       help_text='Configuration versions resolved for the originating job.')
    action = models.CharField(max_length=64)
    reason = models.TextField(blank=True)
    detail = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']


class SourceSnapshot(models.Model):
    """Raw evidence fetched by application code, kept distinct from any agent interpretation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=1000)
    final_url = models.URLField(max_length=1000)
    domain = models.CharField(max_length=255)
    fetched_at = models.DateTimeField()
    http_status = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=120, blank=True)
    sha256 = models.CharField(max_length=64)
    byte_count = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=300, blank=True)
    raw_text = models.TextField(blank=True)
    excerpt = models.TextField(blank=True)
    extraction_notes = models.TextField(blank=True)
    error = models.TextField(blank=True)
    source = models.ForeignKey(Source, null=True, blank=True, on_delete=models.SET_NULL, related_name='snapshots')
    agent_run = models.ForeignKey('AgentRun', null=True, blank=True, on_delete=models.SET_NULL, related_name='snapshots')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title or self.url} ({self.sha256[:8]})'


class Agent(models.Model):
    """A non-human actor with an operator. Distinct from the human operator account."""

    KINDS = [('agent', 'Editorial agent'), ('service', 'Service')]
    SCOPES = [
        ('read', 'Read articles, revisions, proposals and jobs'),
        ('research', 'Start bounded research jobs'),
        ('propose', 'Submit proposals'),
        ('review', 'Record reviews'),
        ('publish_low_risk', 'Reserved. No low-risk publication path is enabled in this pass.'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.SlugField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    kind = models.CharField(max_length=20, choices=KINDS, default='agent')
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT, related_name='agents')
    scopes = models.JSONField(default=list, help_text='Subset of the allowed scopes. Default deny.')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def has_scope(self, scope):
        return self.is_active and scope in (self.scopes or [])


class AgentCredential(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='credentials')
    prefix = models.CharField(max_length=16, unique=True)
    token_hash = models.CharField(max_length=200)
    scopes = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.agent.name} {self.prefix}...'


class AgentRun(models.Model):
    """One model call by one agent profile. Records the model and configuration actually used."""

    STATUS = [('running', 'Running'), ('succeeded', 'Succeeded'), ('failed', 'Failed')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, null=True, blank=True, on_delete=models.SET_NULL, related_name='agent_runs')
    agent = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.SET_NULL, related_name='runs')
    profile = models.CharField(max_length=32)
    role = models.CharField(max_length=40, blank=True)
    model = models.CharField(max_length=160, blank=True)
    model_variant = models.CharField(max_length=40, blank=True)
    config_versions = models.JSONField(default=dict, help_text='Configuration versions and snapshots used.')
    status = models.CharField(max_length=16, choices=STATUS, default='running')
    usage = models.JSONField(default=dict, blank=True)
    usage_measured = models.BooleanField(default=False)
    usage_note = models.CharField(max_length=200, blank=True)
    error = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['started_at']
