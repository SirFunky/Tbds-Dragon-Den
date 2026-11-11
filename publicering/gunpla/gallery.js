(() => {
  const links = Array.from(document.querySelectorAll('a.photo'));
  const dialog = document.querySelector('.lightbox');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  let current = 0;
  let opener;
  const show = index => {
    current = (index + links.length) % links.length;
    const link = links[current];
    dialog.querySelector('img').src = link.href;
    dialog.querySelector('img').alt = link.dataset.caption;
    dialog.querySelector('p').textContent = `${current + 1} / ${links.length} · ${link.dataset.caption}`;
    dialog.querySelector('.original').href = link.href;
  };
  links.forEach((link, index) => link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    opener = link;
    show(index);
    dialog.showModal();
    document.body.classList.add('viewer-open');
  }));
  dialog.querySelector('.close').addEventListener('click', () => dialog.close());
  dialog.querySelector('.previous').addEventListener('click', () => show(current - 1));
  dialog.querySelector('.next').addEventListener('click', () => show(current + 1));
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      show(current + (event.key === 'ArrowLeft' ? -1 : 1));
    }
  });
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => {
    document.body.classList.remove('viewer-open');
    opener?.focus();
  });
})();
