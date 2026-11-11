// Navigation remains fully available when JavaScript is disabled.
(() => {
  const button = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#primary-nav');
  if (!button || !nav) return;
  const narrow = window.matchMedia('(max-width: 900px)');
  const setOpen = (open) => {
    button.setAttribute('aria-expanded', String(open));
    nav.hidden = narrow.matches && !open;
  };
  const reset = () => {
    const restoreFocus = !button.hidden && document.activeElement === button;
    button.hidden = !narrow.matches;
    setOpen(false);
    if (restoreFocus && button.hidden) nav.querySelector('a').focus();
  };
  button.addEventListener('click', () => setOpen(button.getAttribute('aria-expanded') !== 'true'));
  nav.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && narrow.matches) {
      setOpen(false);
      button.focus();
    }
  });
  narrow.addEventListener('change', reset);
  reset();
})();
