"""Bounded source intake for agent research.

The agent may only suggest URLs. This module validates and fetches them, extracts bounded text, and persists a raw
snapshot with a hash. Fetched text is untrusted data; nothing here executes it or treats it as instructions.
"""
import hashlib
import html
import ipaddress
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from html.parser import HTMLParser

from django.utils import timezone

from .models import Source, SourceSnapshot

ALLOWED_CONTENT_TYPES = {'text/html', 'application/xhtml+xml', 'text/plain'}
DEFAULT_UA = 'GalacticaWorkshop/0.2 (local bounded research; contact: operator)'
MAX_URL_LENGTH = 1000


class ResearchError(Exception):
    """Intake refused or failed. The message is safe to show and log."""


def intake_config(data):
    data = data or {}
    domains = data.get('allowed_domains') or []
    if isinstance(domains, str):
        domains = domains.splitlines()
    return {
        'allowed_domains': [str(d).strip().lower() for d in domains if str(d).strip()],
        'max_bytes': max(10000, min(int(data.get('max_bytes', 500000)), 2000000)),
        'timeout_seconds': max(5, min(int(data.get('timeout_seconds', 20)), 60)),
        'max_redirects': max(0, min(int(data.get('max_redirects', 3)), 5)),
        'max_sources': max(1, min(int(data.get('max_sources', 3)), 6)),
        'max_raw_chars': max(10000, min(int(data.get('max_raw_chars', 200000)), 500000)),
        'excerpt_chars': max(300, min(int(data.get('excerpt_chars', 1500)), 4000)),
        'research_instructions': str(data.get('research_instructions', ''))[:3000],
    }


def _host_allowed(host, domains):
    host = (host or '').lower().rstrip('.')
    for domain in domains:
        domain = domain.lower().rstrip('.')
        if host == domain or host.endswith('.' + domain):
            return True
    return False


def _resolve_public(host):
    try:
        infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ResearchError(f'Host did not resolve: {host}') from exc
    addresses = {info[4][0] for info in infos}
    if not addresses:
        raise ResearchError(f'Host did not resolve: {host}')
    for raw in addresses:
        try:
            ip = ipaddress.ip_address(raw)
        except ValueError:
            raise ResearchError('Resolved address was not a valid IP address.')
        if not ip.is_global:
            raise ResearchError('Refused: host resolves to a private, loopback or reserved address.')
    return addresses


def validate_url(url, config):
    """Validate scheme, credentials, port, allowlist and resolved addresses. Returns the normalised URL."""
    if not isinstance(url, str) or len(url) > MAX_URL_LENGTH:
        raise ResearchError('URL is missing or too long.')
    parsed = urllib.parse.urlsplit(url.strip())
    if parsed.scheme != 'https':
        raise ResearchError('Only https:// URLs are accepted.')
    if parsed.username or parsed.password:
        raise ResearchError('URLs with embedded credentials are refused.')
    try:
        port = parsed.port
    except ValueError:
        raise ResearchError('URL has an invalid port.')
    if port not in (None, 443):
        raise ResearchError('Only the default HTTPS port is accepted.')
    host = (parsed.hostname or '').lower()
    if not host or host == 'localhost' or host.endswith('.local'):
        raise ResearchError('Local hostnames are refused.')
    try:
        ipaddress.ip_address(host)
        raise ResearchError('IP-address URLs are refused; use a hostname.')
    except ValueError:
        pass
    if not _host_allowed(host, config['allowed_domains']):
        raise ResearchError(f'Domain is not on the research allowlist: {host}')
    _resolve_public(host)
    cleaned = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path or '/', parsed.query, ''))
    return cleaned


class _BoundedRedirect(urllib.request.HTTPRedirectHandler):
    max_redirections = 3
    max_repeats = 1

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.max_redirections = config['max_redirects']

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urllib.parse.urljoin(req.full_url, newurl)
        validate_url(target, self.config)
        return super().redirect_request(req, fp, code, msg, headers, target)


class _TextExtractor(HTMLParser):
    SKIP = {'script', 'style', 'noscript', 'svg', 'template', 'canvas', 'iframe'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.in_title = False
        self.title_parts = []
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag == 'title':
            self.in_title = True
        elif tag in ('p', 'div', 'section', 'article', 'li', 'br', 'tr', 'h1', 'h2', 'h3', 'h4', 'blockquote'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag == 'title':
            self.in_title = False
        elif tag in ('p', 'div', 'section', 'article', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'blockquote'):
            self.parts.append('\n')

    def handle_data(self, data):
        if self.skip:
            return
        if self.in_title:
            self.title_parts.append(data)
        else:
            self.parts.append(data)


def _normalise(text):
    text = html.unescape(text or '')
    text = re.sub(r'[ \t\r\f\v]+', ' ', text)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    return text.strip()


def extract_text(body_text, content_type, url, config):
    if content_type == 'text/plain':
        text = _normalise(body_text)
        first = next((line.strip() for line in text.splitlines() if line.strip()), '')
        title = first[:300] or urllib.parse.urlsplit(url).hostname
        notes = 'Plain text; whitespace normalised.'
    else:
        parser = _TextExtractor()
        parser.feed(body_text)
        text = _normalise(''.join(parser.parts))
        title = _normalise(''.join(parser.title_parts))[:300] or urllib.parse.urlsplit(url).hostname
        notes = 'HTML text extracted; script/style/noscript/svg/iframe content removed; whitespace normalised.'
    raw = text[:config['max_raw_chars']]
    if len(text) > config['max_raw_chars']:
        notes += f' Stored raw text truncated to {config["max_raw_chars"]} characters.'
    return title, raw, notes


def _excerpt(text, topic, question, size):
    keywords = [w for w in re.findall(r'[a-z0-9]{4,}', f'{topic} {question}'.lower())]
    lowered = text.lower()
    index = -1
    for word in keywords:
        index = lowered.find(word)
        if index != -1:
            break
    if index == -1:
        return text[:size]
    start = max(0, index - 200)
    end = min(len(text), start + size)
    prefix = '…' if start else ''
    suffix = '…' if end < len(text) else ''
    return prefix + text[start:end] + suffix


def fetch_document(url, config):
    """Fetch one URL with no proxies, bounded redirects/bytes/time. Returns a dict or raises ResearchError."""
    final_url = validate_url(url, config)
    request = urllib.request.Request(final_url, headers={
        'User-Agent': DEFAULT_UA,
        'Accept': 'text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.1',
    })
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _BoundedRedirect(config))
    try:
        with opener.open(request, timeout=config['timeout_seconds']) as response:
            status = getattr(response, 'status', 0) or 0
            final_url = validate_url(response.geturl(), config)
            content_type = (response.headers.get_content_type() or '').lower()
            if content_type not in ALLOWED_CONTENT_TYPES:
                raise ResearchError(f'Unsupported content type: {content_type or "unknown"}')
            data = response.read(config['max_bytes'] + 1)
            if len(data) > config['max_bytes']:
                raise ResearchError(f'Page exceeded the {config["max_bytes"]}-byte limit.')
            charset = response.headers.get_content_charset() or 'utf-8'
    except ResearchError:
        raise
    except urllib.error.HTTPError as exc:
        raise ResearchError(f'HTTP error {exc.code} while fetching the source.')
    except urllib.error.URLError as exc:
        reason = getattr(exc, 'reason', exc)
        raise ResearchError(f'Network error while fetching the source: {type(reason).__name__}.')
    except (TimeoutError, socket.timeout):
        raise ResearchError('Fetch timed out.')
    except (ValueError, OSError) as exc:
        raise ResearchError(f'Fetch failed: {type(exc).__name__}.')
    try:
        body_text = data.decode(charset, errors='replace')
    except LookupError:
        body_text = data.decode('utf-8', errors='replace')
    title, raw, notes = extract_text(body_text, content_type, final_url, config)
    return {
        'url': url, 'final_url': final_url, 'domain': urllib.parse.urlsplit(final_url).hostname,
        'http_status': status, 'content_type': content_type,
        'sha256': hashlib.sha256(data).hexdigest(), 'byte_count': len(data),
        'title': title, 'raw_text': raw, 'extraction_notes': notes,
    }


def preserve(url, config, topic, question, *, agent_run=None, fetched_at=None):
    """Fetch and persist a snapshot. Success creates a Source linked to the snapshot. Failures are recorded too."""
    fetched_at = fetched_at or timezone.now()
    try:
        doc = fetch_document(url, config)
    except ResearchError as exc:
        SourceSnapshot.objects.create(
            url=url[:1000], final_url=url[:1000], domain=(urllib.parse.urlsplit(url).hostname or '')[:255],
            fetched_at=fetched_at, sha256='', error=str(exc), agent_run=agent_run,
            extraction_notes='Fetch failed; no content preserved.',
        )
        raise
    snapshot = SourceSnapshot.objects.create(
        url=doc['url'][:1000], final_url=doc['final_url'][:1000], domain=(doc['domain'] or '')[:255],
        fetched_at=fetched_at, http_status=doc['http_status'], content_type=doc['content_type'],
        sha256=doc['sha256'], byte_count=doc['byte_count'], title=doc['title'][:300],
        raw_text=doc['raw_text'], excerpt=_excerpt(doc['raw_text'], topic, question, config['excerpt_chars']),
        extraction_notes=doc['extraction_notes'], agent_run=agent_run,
    )
    source = Source.objects.create(
        title=doc['title'] or doc['final_url'], url=doc['final_url'], kind='web', publisher=doc['domain'] or '',
        published_on='', retrieved_on=date.today(), check_status='fetched',
        retrieval_note=(f'Fetched automatically {fetched_at.isoformat()}; sha256 {doc["sha256"]}; '
                        'not human-verified. Raw snapshot preserved separately.'),
    )
    snapshot.source = source
    snapshot.save(update_fields=['source'])
    return snapshot


def normalise_quote(text):
    return re.sub(r'\s+', ' ', (text or '').lower()).strip()


def quote_in_snapshot(source, quote):
    if not quote:
        return False
    needle = normalise_quote(quote)
    for snapshot in source.snapshots.all():
        if needle and needle in normalise_quote(snapshot.raw_text):
            return True
    return False
