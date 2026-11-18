const spotlight = document.querySelector(".hero-spotlight");
const slideList = spotlight.querySelector(".spotlight-slides");
const slides = [...slideList.children];
const controls = spotlight.querySelector(".spotlight-controls");
const toggle = controls.querySelector("[data-spotlight-toggle]");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const hoverCapable = window.matchMedia("(any-hover: hover)");
let current = 0;
let playing = !reducedMotion.matches;
let timer;

function showSlide(step) {
  slides[current].inert = true;
  current = (current + step + slides.length) % slides.length;
  slides[current].inert = false;
}

function scheduleRotation() {
  window.clearTimeout(timer);
  const paused = !playing || document.hidden || (hoverCapable.matches && spotlight.matches(":hover"))
    || slideList.contains(document.activeElement);
  slideList.setAttribute("aria-live", paused ? "polite" : "off");
  if (!paused) {
    timer = window.setTimeout(() => {
      showSlide(1);
      scheduleRotation();
    }, 4000);
  }
}

function setPlaying(enabled) {
  playing = enabled;
  toggle.textContent = playing ? "Pausa" : "Starta bildspel";
  scheduleRotation();
}

for (const button of controls.querySelectorAll("[data-spotlight-step]")) {
  button.addEventListener("click", () => {
    setPlaying(false);
    showSlide(Number(button.dataset.spotlightStep));
  });
}

toggle.addEventListener("click", () => setPlaying(!playing));
spotlight.addEventListener("mouseenter", scheduleRotation);
spotlight.addEventListener("mouseleave", scheduleRotation);
slideList.addEventListener("focusin", scheduleRotation);
slideList.addEventListener("focusout", () => queueMicrotask(scheduleRotation));
document.addEventListener("visibilitychange", scheduleRotation);
reducedMotion.addEventListener("change", () => setPlaying(!reducedMotion.matches));

controls.hidden = false;
setPlaying(playing);
