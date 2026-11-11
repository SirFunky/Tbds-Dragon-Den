(() => {
  const container = document.getElementById('unit-catalog');
  if (!container) return;
  const data = JSON.parse(document.getElementById('unit-data').textContent);
  const engine = globalThis.IronStarsUnitFilters;
  const form = document.getElementById('unit-filters');
  const controls = Object.fromEntries([...form.elements].filter((el) => el.name).map((el) => [el.name, el]));
  const cards = new Map([...container.querySelectorAll('[data-unit-id]')].map((el) => [el.dataset.unitId, el]));
  const count = document.getElementById('unit-count');
  const empty = document.getElementById('unit-empty');
  const factionNote = document.getElementById('faction-unit-note');
  const pointNote = document.getElementById('point-filter-note');
  const params = new URLSearchParams(location.search);
  const subOptions = [...controls.subfaction.options].map((option) => ({ value: option.value, text: option.textContent }));
  const refreshSubfactions = () => {
    const previous = controls.subfaction.value;
    const allowed = new Set(data.units.filter((u) => !controls.faction.value || u.faction === controls.faction.value).map((u) => u.subfaction || 'unspecified'));
    controls.subfaction.replaceChildren();
    for (const item of subOptions) {
      if (!item.value || allowed.has(item.value)) controls.subfaction.add(new Option(item.text, item.value));
    }
    controls.subfaction.value = allowed.has(previous) ? previous : '';
  };
  for (const name of Object.keys(controls)) {
    if (!params.has(name)) continue;
    const value = params.get(name);
    if (controls[name].tagName !== 'SELECT' || [...controls[name].options].some((o) => o.value === value)) controls[name].value = value;
  }
  refreshSubfactions();
  const update = (save = true) => {
    const filters = Object.fromEntries(Object.entries(controls).map(([name, el]) => [name, el.value]));
    const invalidRange = filters.min !== '' && filters.max !== '' && Number(filters.min) > Number(filters.max);
    controls.max.setCustomValidity(invalidRange ? 'Maximum points must be at least minimum points.' : '');
    const results = invalidRange ? [] : engine.sort(data.units.filter((unit) => engine.matches(unit, filters)), filters.sort);
    const visible = new Set(results.map((unit) => unit.id));
    for (const [id, card] of cards) card.hidden = !visible.has(id);
    for (const unit of results) container.append(cards.get(unit.id));
    count.textContent = invalidRange ? 'Minimum points must not exceed maximum points.' : `${results.length} of ${data.units.length} unit references`;
    empty.hidden = results.length !== 0;
    pointNote.hidden = filters.min === '' && filters.max === '';
    const faction = data.factions.find((f) => f.id === filters.faction);
    if (faction && faction.status !== 'reference') empty.hidden = true;
    factionNote.hidden = !faction || faction.status === 'reference';
    if (faction?.status === 'in-development') factionNote.textContent = `${faction.name} is in development. Its current background and example unit are on the faction page; no full unit profiles or costs have been developed yet.`;
    else if (faction?.status === 'import-roster-pending') factionNote.textContent = 'Southern Cross Compact uses imported stock mechs. Source-faction units appear in this catalog, but no eligible Compact roster or import costs have been assigned here.';
    if (save && location.protocol !== 'file:') {
      const next = new URLSearchParams();
      for (const [key, value] of Object.entries(filters)) if (value && !(key === 'sort' && value === 'name')) next.set(key, value);
      const hash = data.factions.some((f) => '#' + f.id === location.hash) ? '' : location.hash;
      try { history.replaceState(null, '', location.pathname + (next.size ? '?' + next : '') + hash); } catch { /* Filtering remains usable without history access. */ }
    }
  };
  for (const el of Object.values(controls)) el.disabled = false;
  document.getElementById('reset-unit-filters').disabled = false;
  controls.faction.addEventListener('change', () => { refreshSubfactions(); update(); });
  form.addEventListener('input', () => update());
  form.addEventListener('submit', (event) => event.preventDefault());
  form.addEventListener('reset', () => queueMicrotask(() => { refreshSubfactions(); update(); }));
  const applyHashFaction = () => {
    const id = location.hash.slice(1);
    if (data.factions.some((f) => f.id === id)) {
      controls.faction.value = id; refreshSubfactions(); update(false);
    }
  };
  window.addEventListener('hashchange', applyHashFaction);
  update(false); applyHashFaction();
})();
