from django.contrib import admin

from .models import (
    Agent, AgentCredential, AgentRun, Article, AuditEvent, Block, Citation, ConfigVersion, EvalCase, EvalResult, Job,
    JobEvent, Proposal, Review, Revision, Source, SourceSnapshot,
)


class ReadOnlyAdmin(admin.ModelAdmin):
    """Published content and history are changed only through services, never through admin forms."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class BlockInline(admin.TabularInline):
    model = Block
    extra = 0
    readonly_fields = ('block_id', 'position', 'kind', 'data')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'provenance', 'published', 'updated_at')
    list_filter = ('provenance',)
    search_fields = ('title', 'slug', 'opening')
    readonly_fields = ('published', 'created_at', 'updated_at')


@admin.register(Revision)
class RevisionAdmin(ReadOnlyAdmin):
    list_display = ('article', 'number', 'state', 'title', 'created_by', 'created_at', 'published_at')
    list_filter = ('state', 'article')
    search_fields = ('title', 'article__slug', 'summary')
    readonly_fields = ('article', 'number', 'state', 'title', 'opening', 'summary', 'reverts', 'content_hash',
                       'created_by', 'created_at', 'published_at')
    inlines = [BlockInline]


@admin.register(Proposal)
class ProposalAdmin(ReadOnlyAdmin):
    list_display = ('article', 'status', 'origin', 'agent', 'base', 'created_by', 'created_at', 'decided_by')
    list_filter = ('status', 'origin', 'article')
    search_fields = ('rationale', 'article__slug')
    readonly_fields = ('article', 'base', 'candidate', 'status', 'origin', 'rationale', 'repeat_of', 'eval_case',
                       'result', 'created_by', 'agent', 'origin_job', 'origin_model', 'created_at', 'decided_by',
                       'decided_at', 'decision_note')


@admin.register(Review)
class ReviewAdmin(ReadOnlyAdmin):
    list_display = ('proposal', 'role', 'verdict', 'origin', 'agent', 'declared_model', 'created_at')
    list_filter = ('role', 'verdict', 'origin')
    readonly_fields = ('proposal', 'role', 'verdict', 'comment', 'evidence_notes', 'origin', 'declared_model', 'agent',
                       'agent_run', 'job', 'created_at')


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'operator', 'is_active', 'scopes', 'created_at')
    list_filter = ('kind', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at')


@admin.register(AgentCredential)
class AgentCredentialAdmin(ReadOnlyAdmin):
    list_display = ('agent', 'prefix', 'scopes', 'created_at', 'last_used_at', 'revoked_at')
    list_filter = ('revoked_at',)
    readonly_fields = ('agent', 'prefix', 'token_hash', 'scopes', 'created_at', 'last_used_at', 'revoked_at')


@admin.register(AgentRun)
class AgentRunAdmin(ReadOnlyAdmin):
    list_display = ('agent', 'profile', 'role', 'model', 'status', 'job', 'started_at')
    list_filter = ('profile', 'status')
    search_fields = ('model', 'role', 'error')


@admin.register(SourceSnapshot)
class SourceSnapshotAdmin(ReadOnlyAdmin):
    list_display = ('title', 'domain', 'fetched_at', 'http_status', 'byte_count', 'sha256', 'agent_run')
    list_filter = ('domain', 'http_status')
    search_fields = ('title', 'url', 'final_url', 'sha256')


@admin.register(Job)
class JobAdmin(ReadOnlyAdmin):
    list_display = ('label', 'kind', 'runner', 'status', 'created_at', 'finished_at')
    list_filter = ('status', 'kind', 'runner')
    search_fields = ('label', 'error')
    readonly_fields = ('kind', 'status', 'runner', 'label', 'article', 'proposal', 'input', 'config_snapshot', 'output',
                       'usage', 'error', 'cancel_requested', 'retry_of', 'model_calls', 'max_model_calls',
                       'timeout_seconds', 'worker_id', 'created_by', 'created_at', 'started_at', 'heartbeat_at',
                       'finished_at')


@admin.register(JobEvent)
class JobEventAdmin(ReadOnlyAdmin):
    list_display = ('job', 'created_at', 'level', 'message')
    list_filter = ('level',)


@admin.register(AuditEvent)
class AuditEventAdmin(ReadOnlyAdmin):
    list_display = ('article', 'action', 'actor', 'agent', 'model', 'revision', 'created_at')
    list_filter = ('action', 'agent')
    search_fields = ('reason', 'article__slug')


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'check_status', 'publisher', 'published_on', 'retrieved_on')
    list_filter = ('kind', 'check_status')
    search_fields = ('title', 'url', 'authors', 'publisher')


@admin.register(Citation)
class CitationAdmin(ReadOnlyAdmin):
    list_display = ('revision', 'source', 'block_id')
    search_fields = ('supports', 'source__title')


@admin.register(ConfigVersion)
class ConfigVersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'family', 'version', 'is_default', 'provisional', 'created_at')
    list_filter = ('kind', 'is_default', 'provisional')
    search_fields = ('name', 'family', 'description')


@admin.register(EvalCase)
class EvalCaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'article', 'expected', 'label_source')
    list_filter = ('category', 'expected', 'label_source')
    search_fields = ('name', 'description')


@admin.register(EvalResult)
class EvalResultAdmin(ReadOnlyAdmin):
    list_display = ('case', 'candidate_label', 'outcome', 'expected', 'matches', 'job')
    list_filter = ('outcome', 'matches')
