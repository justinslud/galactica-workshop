"""Validation for article blocks. Every write path (editor, services, seed) goes through here."""
import re
import uuid

from django.core.exceptions import ValidationError

MAX_MARKDOWN = 20000
MAX_BLOCKS = 40
MAX_SOURCE_PREFIXES = ('/static/', 'https://')


def _text(value, field, *, max_len, required=True):
    if value is None:
        value = ''
    if not isinstance(value, str):
        raise ValidationError(f'{field} must be text.')
    value = value.strip()
    if required and not value:
        raise ValidationError(f'{field} is required.')
    if len(value) > max_len:
        raise ValidationError(f'{field} is longer than {max_len} characters.')
    return value


def _validate_markdown(data):
    return {'text': _text(data.get('text'), 'Text', max_len=MAX_MARKDOWN)}


def _validate_image(data):
    src = _text(data.get('src'), 'Image source', max_len=300)
    if not src.startswith(MAX_SOURCE_PREFIXES):
        raise ValidationError('Image source must be a /static/ path or an https:// URL.')
    if re.search(r'[\s"<>]', src):
        raise ValidationError('Image source must not contain spaces, quotes or angle brackets.')
    return {
        'src': src,
        'alt': _text(data.get('alt'), 'Alt text', max_len=300),
        'caption': _text(data.get('caption'), 'Caption', max_len=300, required=False),
        'credit': _text(data.get('credit'), 'Credit', max_len=300),
    }


def _validate_table(data):
    headers = data.get('headers')
    rows = data.get('rows', [])
    if not isinstance(headers, list) or not 1 <= len(headers) <= 8:
        raise ValidationError('A table needs between 1 and 8 header cells.')
    headers = [_text(h, 'Table header', max_len=120) for h in headers]
    if not isinstance(rows, list) or len(rows) > 40:
        raise ValidationError('A table can have at most 40 rows.')
    clean_rows = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, list) or len(row) != len(headers):
            raise ValidationError(f'Table row {index} must have exactly {len(headers)} cells.')
        clean_rows.append([_text(c, f'Row {index} cell', max_len=300, required=False) for c in row])
    return {
        'caption': _text(data.get('caption'), 'Table caption', max_len=200),
        'headers': headers,
        'rows': clean_rows,
    }


def _validate_timeline(data):
    events = data.get('events')
    if not isinstance(events, list) or not 1 <= len(events) <= 20:
        raise ValidationError('A timeline needs between 1 and 20 events.')
    clean = []
    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            raise ValidationError(f'Timeline event {index} is malformed.')
        clean.append({
            'date': _text(event.get('date'), f'Event {index} date', max_len=40),
            'text': _text(event.get('text'), f'Event {index} text', max_len=400),
        })
    return {'title': _text(data.get('title'), 'Timeline title', max_len=120), 'events': clean}


VALIDATORS = {
    'markdown': _validate_markdown,
    'image': _validate_image,
    'table': _validate_table,
    'timeline': _validate_timeline,
}


def validate_block(kind, data):
    """Return normalized data for one block or raise ValidationError."""
    if kind not in VALIDATORS:
        raise ValidationError(f'Unknown block type: {kind}.')
    if not isinstance(data, dict):
        raise ValidationError(f'{kind} block data must be an object.')
    return VALIDATORS[kind](data)


def validate_blocks(items):
    """items: list of {'block_id': str, 'kind': str, 'data': dict}. Returns normalized list.

    New blocks may omit block_id; a fresh stable id is then assigned by the caller.
    """
    if not isinstance(items, list):
        raise ValidationError('Blocks must be a list.')
    if not 1 <= len(items) <= MAX_BLOCKS:
        raise ValidationError(f'An article needs between 1 and {MAX_BLOCKS} blocks.')
    seen = set()
    result = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValidationError(f'Block {index} is malformed.')
        raw_id = item.get('block_id')
        if raw_id:
            try:
                block_id = str(uuid.UUID(str(raw_id)))
            except ValueError:
                raise ValidationError(f'Block {index} has an invalid id.')
            if block_id in seen:
                raise ValidationError(f'Block {index} repeats an id already used.')
            seen.add(block_id)
        else:
            block_id = None
        try:
            data = validate_block(item.get('kind'), item.get('data'))
        except ValidationError as exc:
            message = ' '.join(exc.messages)
            raise ValidationError(f'Block {index}: {message}')
        result.append({'block_id': block_id, 'kind': item.get('kind'), 'data': data})
    return result
