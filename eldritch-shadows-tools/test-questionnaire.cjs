// Dependency-free DOM harness for questionnaire behavior; not a visual browser test.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync('Eldritch shadows/questionnaire.html', 'utf8');
const script = fs.readFileSync('Eldritch shadows/questionnaire.js', 'utf8');
const decode = value => value.replaceAll('&amp;', '&').replaceAll('&quot;', '"').replaceAll('&lt;', '<');
class Element {
  constructor(tag, attrs = {}) { this.tagName = tag.toUpperCase(); this.attrs = attrs; this.children = []; this.events = {}; this.style = {}; this.checked = false; this.disabled = false; this.value = attrs.value || ''; this.name = attrs.name; this.type = attrs.type; this.id = attrs.id; this.className = attrs.class || ''; this.dataset = Object.fromEntries(Object.entries(attrs).filter(([key]) => key.startsWith('data-')).map(([key, value]) => [key.slice(5), value])); this.scrollHeight = 100; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  get childElementCount() { return this.children.filter(child => child instanceof Element).length; }
  set textContent(value) { this.children = [value]; }
  get textContent() { return this.children.map(child => child instanceof Element ? child.textContent : child).join(''); }
  matches(selector) {
    const tag = selector.match(/^[a-z][a-z0-9]*/i)?.[0];
    if (tag && this.tagName !== tag.toUpperCase()) return false;
    const cls = selector.match(/\.([\w-]+)/)?.[1];
    if (cls && !this.className.split(' ').includes(cls)) return false;
    for (const [, key, value] of selector.matchAll(/\[([\w-]+)(?:="([^"]*)")?\]/g)) {
      if (!(key in this.attrs) || (value !== undefined && this.attrs[key] !== value)) return false;
    }
    if (selector.includes(':checked') && !this.checked) return false;
    return true;
  }
  querySelectorAll(selector) {
    const result = [];
    for (const child of this.children) if (child instanceof Element) {
      if (selector.split(',').some(part => child.matches(part.trim()))) result.push(child);
      result.push(...child.querySelectorAll(selector));
    }
    return result;
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
  addEventListener(type, callback) { this.events[type] = callback; }
  click() { this.events.click?.(); }
}
function boot(saved, blocked = false) {
  const document = new Element('document');
  const stack = [document];
  for (const token of html.match(/<[^>]+>|[^<]+/g)) {
    if (token.startsWith('<!')) continue;
    if (token.startsWith('</')) { stack.pop(); continue; }
    if (!token.startsWith('<')) { stack.at(-1).append(decode(token)); continue; }
    const tag = token.match(/^<([\w-]+)/)[1];
    const attrs = Object.fromEntries([...token.matchAll(/([\w-]+)="([^"]*)"/g)].map(([, key, value]) => [key, decode(value)]));
    const el = new Element(tag, attrs);
    stack.at(-1).append(el);
    if (!['input','img','meta','link','br'].includes(tag)) stack.push(el);
  }
  document.getElementById = id => document.querySelectorAll('[id]').find(el => el.id === id);
  document.createElement = tag => {
    const el = new Element(tag);
    for (const key of ['name','type','value']) Object.defineProperty(el, key, { get: () => el.attrs[key], set: value => { el.attrs[key] = value; } });
    return el;
  };
  let stored = saved, blob, printed = false;
  const window = { addEventListener() {}, print() { printed = true; } };
  vm.runInNewContext(script, { document, window, localStorage: { getItem() { if (blocked) throw Error('blocked'); return stored; }, setItem(key, value) { if (blocked) throw Error('blocked'); stored = value; } }, Blob, URL: { createObjectURL(value) { blob = value; return 'blob:test'; }, revokeObjectURL() {} }, setTimeout: fn => fn() });
  const form = document.getElementById('questionnaire');
  function choose(name, value, checked = true) {
    const field = form.querySelectorAll('input').find(el => el.name === name && el.value === value);
    assert.ok(field, `${name}: ${value} exists`);
    if (field.type === 'radio') for (const peer of form.querySelectorAll('input').filter(el => el.name === name)) peer.checked = false;
    field.checked = checked;
    form.events.change();
    return field;
  }
  return { document, form, choose, stored: () => stored, blob: () => blob, printed: () => printed };
}
(async () => {
  const app = boot();
  for (const n of [1,10,11,12,21]) {
    const box = app.document.getElementById(`q${n}-other`);
    assert.equal(box.hidden, true);
    app.choose(`q${n}`, 'Other');
    assert.equal(box.hidden, false);
    box.querySelector('textarea').value = 'Specific detail';
    const first = app.form.querySelectorAll('input').find(el => el.name === `q${n}` && el.value !== 'Other');
    app.choose(`q${n}`, first.value);
    assert.equal(box.hidden, true);
    assert.equal(JSON.parse(app.stored())[`q${n}_other`], undefined);
  }
  assert.equal(app.document.getElementById('q11_detail').disabled, false);
  app.choose('q17', 'Yes');
  assert.equal(app.document.getElementById('q17-detail').hidden, false);
  app.choose('q17', 'No');
  assert.equal(app.document.getElementById('q17-detail').hidden, true);
  app.choose('q6', 'Debt'); app.choose('q6', 'Addiction');
  assert.equal(JSON.parse(app.stored()).q6.length, 2);
  app.choose('q15', 'Eldritch'); app.choose('q15', 'Void');
  assert.deepEqual(app.document.getElementById('q16-options').querySelectorAll('input').map(el => el.value), ['Eldritch','Void']);
  const q16 = app.choose('q16', 'Void');
  assert.equal(app.document.getElementById('q16-options').querySelectorAll('input')[1], q16, 'Q16 keeps focusable nodes on selection');
  app.choose('q16_reaction', 'Draws me in');
  app.document.getElementById('q18').value = 'Long optional answer';
  app.form.events.input();
  const restored = boot(app.stored());
  assert.equal(restored.form.querySelector('input[name="q16"]:checked').value, 'Void');
  assert.equal(restored.document.getElementById('q18').value, 'Long optional answer');
  restored.document.getElementById('download-answers').click();
  const text = await restored.blob().text();
  assert.ok(text.includes('Debt; Addiction'));
  assert.ok(text.includes('Reaction: Draws me in'));
  assert.ok(text.includes('Long optional answer'));
  assert.ok(!text.includes('Specific detail'));
  restored.document.getElementById('print-answers').click();
  assert.equal(restored.printed(), true);
  app.choose('q15', 'Void', false);
  assert.equal(app.form.querySelector('input[name="q16"]:checked'), null);
  app.choose('q15', 'Eldritch', false);
  assert.equal(app.form.querySelector('.reaction').disabled, true);
  assert.equal(app.form.querySelector('input[name="q16_reaction"]:checked'), null);
  assert.ok(boot('{broken').document.getElementById('save-status').textContent.includes('could not be loaded'));
  assert.ok(boot(null, true).document.getElementById('save-status').textContent.includes('could not be loaded'));
  console.log('PASS: conditional details, independent checkboxes, Q15/Q16 dependencies and keyboard node stability, save/restore, text export, print action, invalid/blocked storage');
})();
