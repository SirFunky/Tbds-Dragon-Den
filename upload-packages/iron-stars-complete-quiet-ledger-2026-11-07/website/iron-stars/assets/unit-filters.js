// Shared pure filtering functions; no network calls or framework dependencies.
((root) => {
  const normalize = (value) => String(value || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const matches = (unit, filters = {}) => {
    if (filters.faction && unit.faction !== filters.faction) return false;
    if (filters.subfaction && (unit.subfaction || 'unspecified') !== filters.subfaction) return false;
    if (filters.role && !unit.role_tags.includes(filters.role)) return false;
    if (filters.status === 'review' && !unit.review_notes.length) return false;
    if (filters.status === 'clear' && unit.review_notes.length) return false;
    const bounded = filters.min !== '' && filters.min != null || filters.max !== '' && filters.max != null;
    const points = unit.points.filter_value;
    if (bounded && (points == null || !Number.isFinite(points))) return false;
    if (filters.min !== '' && filters.min != null && points < Number(filters.min)) return false;
    if (filters.max !== '' && filters.max != null && points > Number(filters.max)) return false;
    const words = normalize(filters.query).split(/\s+/).filter(Boolean);
    const text = normalize([unit.name, unit.faction_name, unit.subfaction, unit.role?.text, unit.chassis?.text,
      ...unit.weapons.map((weapon) => [weapon.name_context, weapon.text || weapon.cells.map((cell) => cell.text).join(' ')].filter(Boolean).join(' ')),
      ...unit.systems.map((system) => system.name)].join(' '));
    return words.every((word) => text.includes(word));
  };
  const sort = (units, order = 'name') => [...units].sort((a, b) => {
    if (order.startsWith('points')) {
      const av = a.points.filter_value; const bv = b.points.filter_value;
      if (av == null && bv != null) return 1;
      if (bv == null && av != null) return -1;
      if (av != null && bv != null && av !== bv) return order === 'points-desc' ? bv - av : av - bv;
    }
    return a.name.localeCompare(b.name);
  });
  const api = { normalize, matches, sort };
  root.IronStarsUnitFilters = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(globalThis);
