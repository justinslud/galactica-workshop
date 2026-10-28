// Block editor for Galactica. Plain JavaScript, no framework.
// The server validates everything; this file only shapes the payload and shows the live preview.
(function () {
  'use strict';
  var form = document.getElementById('editor-form');
  if (!form) { return; }

  var initial = JSON.parse(document.getElementById('initial-payload').textContent);
  var sources = JSON.parse(document.getElementById('sources-data').textContent);
  var previewUrl = form.getAttribute('data-preview-url');
  var blocksEl = document.getElementById('blocks');
  var saveState = document.getElementById('save-state');
  var previewBody = document.getElementById('preview-body');
  var previewErrors = document.getElementById('preview-errors');
  var payloadField = document.getElementById('payload');
  var rationale = document.getElementById('rationale');
  var titleInput = document.getElementById('ed-title');
  var openingInput = document.getElementById('ed-opening');
  var timer = null;
  var KIND_LABEL = { markdown: 'Text', image: 'Image', table: 'Table', timeline: 'Timeline' };
  var DEFAULTS = {
    markdown: function () { return { text: '## New section\n\nWrite here.' }; },
    image: function () { return { src: '/static/img/', alt: '', caption: '', credit: '' }; },
    table: function () { return { caption: '', headers: ['Column 1', 'Column 2'], rows: [['', '']] }; },
    timeline: function () { return { title: '', events: [{ date: '', text: '' }] }; }
  };

  function clone(value) { return JSON.parse(JSON.stringify(value)); }
  function newId() {
    if (window.crypto && window.crypto.randomUUID) { return window.crypto.randomUUID(); }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      var r = Math.random() * 16 | 0; return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
  }

  var state = {
    title: initial.title, opening: initial.opening, version: initial.version,
    blocks: initial.blocks.map(clone), citations: initial.citations.map(clone)
  };
  var savedSnapshot = JSON.stringify(serialize());

  function serialize() {
    return { title: state.title, opening: state.opening, version: state.version,
             blocks: state.blocks, citations: state.citations };
  }
  function isDirty() { return JSON.stringify(serialize()) !== savedSnapshot; }
  function markState() {
    var dirty = isDirty();
    saveState.textContent = dirty ? 'Unsaved changes' : 'All changes saved';
    saveState.className = 'save-state ' + (dirty ? 'dirty' : 'clean');
  }
  function csrf() {
    var el = form.querySelector('input[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
  }

  function schedulePreview() {
    markState();
    window.clearTimeout(timer);
    timer = window.setTimeout(renderPreview, 350);
  }

  function renderPreview() {
    var body = { title: state.title, opening: state.opening, blocks: state.blocks, citations: state.citations };
    fetch(previewUrl, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
      body: JSON.stringify(body)
    }).then(function (response) {
      return response.json().then(function (data) { return { ok: response.ok, data: data }; });
    }).then(function (result) {
      previewErrors.innerHTML = '';
      if (result.data.errors && result.data.errors.length) {
        result.data.errors.forEach(function (msg) {
          var p = document.createElement('p'); p.textContent = msg; previewErrors.appendChild(p);
        });
      }
      previewBody.innerHTML = result.data.html || '';
    }).catch(function () {
      previewErrors.textContent = 'Preview unavailable. Check that the web app is running.';
    });
  }

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'text') { node.textContent = attrs[k]; }
      else if (k === 'className') { node.className = attrs[k]; }
      else if (k.indexOf('on') === 0) { node.addEventListener(k.slice(2), attrs[k]); }
      else { node.setAttribute(k, attrs[k]); }
    });
    (children || []).forEach(function (c) { if (c) { node.appendChild(c); } });
    return node;
  }

  function field(label, input) {
    return el('label', { className: 'stacked' }, [el('span', { text: label }), input]);
  }

  function textInput(value, onChange, attrs) {
    var input = el('input', Object.assign({ type: 'text', value: value || '' }, attrs || {}));
    input.addEventListener('input', function () { onChange(input.value); schedulePreview(); });
    return input;
  }

  function textArea(value, onChange, rows) {
    var area = el('textarea', { rows: String(rows || 3) });
    area.value = value || '';
    area.addEventListener('input', function () { onChange(area.value); schedulePreview(); });
    return area;
  }

  function formatSelection(area, kind) {
    var start = area.selectionStart, end = area.selectionEnd;
    var before = area.value.slice(0, start), selected = area.value.slice(start, end), after = area.value.slice(end);
    var text = selected || 'text';
    var out = {
      bold: ['**' + text + '**', 2], italic: ['*' + text + '*', 1], code: ['`' + text + '`', 1],
      heading: ['## ' + text, 3], list: ['- ' + text, 2],
      link: ['[' + text + '](https://)', 1],
      explain: ['<details>\n<summary>Explanation</summary>\n\n' + text + '\n\n</details>', 0]
    }[kind];
    if (!out) { return; }
    area.value = before + out[0] + after;
    var caret = before.length + out[0].length - (out[1] || 0);
    area.focus();
    area.setSelectionRange(caret, caret);
    area.dispatchEvent(new Event('input'));
  }

  function markdownEditor(block) {
    var area = textArea(block.data.text, function (v) { block.data.text = v; }, 10);
    var toolbar = el('div', { className: 'toolbar', role: 'toolbar', 'aria-label': 'Formatting' });
    [['bold', 'B'], ['italic', 'I'], ['heading', 'H2'], ['list', 'List'], ['link', 'Link'], ['code', 'Code'],
     ['explain', 'Explanation']].forEach(function (pair) {
      toolbar.appendChild(el('button', {
        type: 'button', className: 'btn btn-tiny', text: pair[1], title: pair[0],
        onclick: function () { formatSelection(area, pair[0]); }
      }));
    });
    return el('div', { className: 'block-fields' }, [toolbar, area,
      el('p', { className: 'help', text: 'Markdown. Raw HTML is removed; use the Explanation button for expandable notes.' })]);
  }

  function imageEditor(block) {
    var d = block.data;
    return el('div', { className: 'block-fields grid-fields' }, [
      field('Image path or https URL', textInput(d.src, function (v) { d.src = v; }, { placeholder: '/static/img/...' })),
      field('Alt text (describe the picture)', textInput(d.alt, function (v) { d.alt = v; })),
      field('Caption', textInput(d.caption, function (v) { d.caption = v; })),
      field('Credit (source of the image)', textInput(d.credit, function (v) { d.credit = v; }))
    ]);
  }

  function tableEditor(block) {
    var d = block.data;
    var rowsText = d.rows.map(function (r) { return r.join(' | '); }).join('\n');
    return el('div', { className: 'block-fields grid-fields' }, [
      field('Caption', textInput(d.caption, function (v) { d.caption = v; })),
      field('Headers (comma separated)', textInput(d.headers.join(', '), function (v) {
        d.headers = v.split(',').map(function (s) { return s.trim(); }).filter(Boolean);
      })),
      el('label', { className: 'stacked wide' }, [
        el('span', { text: 'Rows: one row per line, cells separated by " | "' }),
        textArea(rowsText, function (v) {
          d.rows = v.split('\n').filter(function (l) { return l.trim() !== ''; })
            .map(function (l) { return l.split('|').map(function (c) { return c.trim(); }); });
        }, 5)
      ])
    ]);
  }

  function timelineEditor(block) {
    var d = block.data;
    var eventsText = d.events.map(function (e) { return e.date + ' | ' + e.text; }).join('\n');
    return el('div', { className: 'block-fields grid-fields' }, [
      field('Timeline title', textInput(d.title, function (v) { d.title = v; })),
      el('label', { className: 'stacked wide' }, [
        el('span', { text: 'Events: one per line as "date | what happened"' }),
        textArea(eventsText, function (v) {
          d.events = v.split('\n').filter(function (l) { return l.trim() !== ''; }).map(function (l) {
            var cut = l.indexOf('|');
            return cut === -1 ? { date: '', text: l.trim() } : { date: l.slice(0, cut).trim(), text: l.slice(cut + 1).trim() };
          });
        }, 6)
      ])
    ]);
  }

  var EDITORS = { markdown: markdownEditor, image: imageEditor, table: tableEditor, timeline: timelineEditor };

  function evidenceSection(block) {
    var wrap = el('div', { className: 'evidence-edit' });
    wrap.appendChild(el('h4', { text: 'Evidence for this block' }));
    var mine = state.citations.filter(function (c) { return c.block_id === block.block_id; });
    mine.forEach(function (c) {
      var select = el('select');
      sources.forEach(function (s) {
        var opt = el('option', { value: s.id, text: s.title + ' (' + s.check + ')' });
        if (s.id === c.source_id) { opt.selected = true; }
        select.appendChild(opt);
      });
      select.addEventListener('change', function () { c.source_id = select.value; schedulePreview(); });
      var supports = textInput(c.supports, function (v) { c.supports = v; }, { placeholder: 'What does this source support?' });
      var quote = textInput(c.quote, function (v) { c.quote = v; }, { placeholder: 'Short quote, only if checked (optional)' });
      var remove = el('button', { type: 'button', className: 'btn btn-tiny btn-danger', text: 'Remove evidence',
        onclick: function () { state.citations = state.citations.filter(function (x) { return x !== c; }); renderBlocks(); schedulePreview(); } });
      wrap.appendChild(el('div', { className: 'evidence-row' }, [field('Source', select), field('Supports', supports), field('Quote', quote), remove]));
    });
    var addBtn = el('button', { type: 'button', className: 'btn btn-tiny', text: '+ Attach source',
      onclick: function () {
        if (!sources.length) { window.alert('Add a source first (Sources link on the editor page).'); return; }
        state.citations.push({ block_id: block.block_id, source_id: sources[0].id, supports: '', quote: '' });
        renderBlocks(); schedulePreview();
      } });
    wrap.appendChild(addBtn);
    if (!sources.length) {
      wrap.appendChild(el('a', { href: '/sources/new/?next=' + encodeURIComponent(window.location.pathname), className: 'btn btn-tiny btn-quiet', text: 'Add a source' }));
    }
    return wrap;
  }

  function moveBlock(index, delta) {
    var target = index + delta;
    if (target < 0 || target >= state.blocks.length) { return; }
    var tmp = state.blocks[index];
    state.blocks[index] = state.blocks[target];
    state.blocks[target] = tmp;
    renderBlocks(); schedulePreview();
  }

  function removeBlock(index) {
    var block = state.blocks[index];
    var attached = state.citations.filter(function (c) { return c.block_id === block.block_id; }).length;
    var note = attached ? ' It also removes ' + attached + ' evidence link(s).' : '';
    if (!window.confirm('Remove this block?' + note + ' You can undo by reloading before saving.')) { return; }
    state.citations = state.citations.filter(function (c) { return c.block_id !== block.block_id; });
    state.blocks.splice(index, 1);
    renderBlocks(); schedulePreview();
  }

  function blockCard(block, index) {
    var head = el('div', { className: 'block-head' }, [
      el('strong', { text: index + 1 + '. ' + (KIND_LABEL[block.kind] || block.kind) }),
      el('span', { className: 'spacer' }),
      el('button', { type: 'button', className: 'btn btn-tiny', text: 'Up', disabled: index === 0 ? 'disabled' : null,
        onclick: function () { moveBlock(index, -1); } }),
      el('button', { type: 'button', className: 'btn btn-tiny', text: 'Down', disabled: index === state.blocks.length - 1 ? 'disabled' : null,
        onclick: function () { moveBlock(index, 1); } }),
      el('button', { type: 'button', className: 'btn btn-tiny btn-danger', text: 'Remove',
        onclick: function () { removeBlock(index); } })
    ].filter(Boolean));
    var editor = (EDITORS[block.kind] || function () { return el('p', { text: 'Unsupported block type.' }); })(block);
    return el('article', { className: 'block-card', 'data-block-id': block.block_id }, [head, editor, evidenceSection(block)]);
  }

  function renderBlocks() {
    blocksEl.innerHTML = '';
    if (!state.blocks.length) {
      blocksEl.appendChild(el('p', { className: 'empty-inline', text: 'No blocks. Add one below.' }));
    }
    state.blocks.forEach(function (block, index) { blocksEl.appendChild(blockCard(block, index)); });
    markState();
  }

  document.querySelectorAll('[data-add]').forEach(function (button) {
    button.addEventListener('click', function () {
      var kind = button.getAttribute('data-add');
      state.blocks.push({ block_id: newId(), kind: kind, data: DEFAULTS[kind]() });
      renderBlocks(); schedulePreview();
    });
  });

  titleInput.value = state.title;
  openingInput.value = state.opening;
  titleInput.addEventListener('input', function () { state.title = titleInput.value; schedulePreview(); });
  openingInput.addEventListener('input', function () { state.opening = openingInput.value; schedulePreview(); });

  form.addEventListener('submit', function (event) {
    var submitting = document.activeElement && document.activeElement.value === 'submit';
    rationale.required = !!submitting;
    rationale.minLength = submitting ? 20 : 0;
    payloadField.value = JSON.stringify(serialize());
    window.onbeforeunload = null;
    if (!submitting) { return; }
    if (rationale.value.trim().length < 20) {
      event.preventDefault();
      rationale.reportValidity();
    }
  });

  window.addEventListener('beforeunload', function (event) {
    if (isDirty()) { event.preventDefault(); event.returnValue = ''; }
  });

  renderBlocks();
  renderPreview();
})();
