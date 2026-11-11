(() => {
  const form = document.getElementById('armory-filters');
  const cards = [...document.querySelectorAll('.armory-card')];
  const search = document.getElementById('armory-search');
  const controls = ['kind', 'source', 'priced'].map(k => [k, document.getElementById(`armory-${k}`)]);
  const searchable = cards.map(c => c.textContent.toLocaleLowerCase());
  function filter() {
    const words = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let count = 0;
    cards.forEach((card, i) => {
      const show = words.every(w => searchable[i].includes(w)) && controls.every(([k, el]) => !el.value || card.dataset[k] === el.value);
      card.hidden = !show;
      if (show) count++;
    });
    document.getElementById('armory-count').textContent = `${count} of ${cards.length} components`;
    document.getElementById('armory-empty').hidden = count !== 0;
  }
  form.addEventListener('submit', e => e.preventDefault());
  form.addEventListener('input', filter);
  form.addEventListener('change', filter);
  form.addEventListener('reset', () => setTimeout(filter, 0));
  filter();
})();
