const modal=document.querySelector('dialog');
let trigger;
document.querySelectorAll('.zoom').forEach(link=>link.addEventListener('click',event=>{
  if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
  event.preventDefault();trigger=link;
  const image=link.querySelector('img');
  modal.querySelector('img').src=link.href;
  modal.querySelector('img').alt=image.alt;
  modal.querySelector('p').textContent=image.alt;
  modal.querySelector('.original').href=link.href;
  modal.showModal();document.body.style.overflow='hidden';
}));
modal.querySelector('.close').addEventListener('click',()=>modal.close());
modal.addEventListener('click',event=>{if(event.target===modal){const r=modal.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)modal.close();}});
modal.addEventListener('close',()=>{document.body.style.overflow='';trigger?.focus();});
