(() => {
  const input = document.getElementById('rule-search');
  if (!input) return;
  const clear = document.getElementById('clear-search');
  const results = document.getElementById('search-results');
  const status = document.getElementById('search-status');
  const print = document.querySelector('.print-rules');
  const normalize = (text) => text.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const entries = Array.from(document.querySelectorAll('[data-search-entry]')).map((element) => {
    const text = Array.from(element.querySelectorAll('.source-text')).map((node) => node.textContent).join(' ').replace(/\s+/g, ' ').trim();
    return { id: element.id, title: element.dataset.searchTitle, text, searchable: normalize(element.dataset.searchTitle + ' ' + text) };
  });
  const search = () => {
    const query = input.value.trim();
    results.replaceChildren();
    if (!query) {
      results.hidden = true;
      clear.disabled = true;
      status.textContent = 'Search the entire core rulebook. All chapters remain visible below.';
      return;
    }
    clear.disabled = false;
    const terms = normalize(query).split(/\s+/).filter(Boolean);
    const matches = entries.filter((entry) => terms.every((term) => entry.searchable.includes(term)));
    results.hidden = false;
    status.textContent = matches.length ? `${matches.length} matching ${matches.length === 1 ? 'passage' : 'passages'}.${matches.length > 50 ? ' Showing the first 50; add words to narrow your search.' : ''}` : 'No matching rules. Try a shorter phrase or open the keyword glossary.';
    for (const entry of matches.slice(0, 50)) {
      const item = document.createElement('li');
      const link = document.createElement('a');
      link.href = '#' + entry.id;
      link.textContent = entry.title;
      const preview = document.createElement('p');
      const index = normalize(entry.text).indexOf(terms[0]);
      const start = Math.max(0, index - 45);
      const excerpt = entry.text.slice(start, start + 240);
      preview.textContent = (start ? '…' : '') + excerpt + (start + 240 < entry.text.length ? '…' : '');
      item.append(link, preview);
      results.append(item);
    }
  };
  input.disabled = false;
  input.addEventListener('input', search);
  input.addEventListener('search', search);
  clear.addEventListener('click', () => { input.value = ''; search(); input.focus(); });
  print.hidden = false;
  print.addEventListener('click', () => window.print());
  // Explicit tabindex allows keyboard users to follow search links into tables
  // and paragraphs, with focus and context preserved after fragment navigation.
  const focusHash = () => {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (target && document.querySelector('.rulebook-body').contains(target)) {
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    }
  };
  window.addEventListener('hashchange', focusHash);
  focusHash();
  search();
})();
