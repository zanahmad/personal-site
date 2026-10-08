(() => {
  'use strict';
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const figures = document.querySelectorAll('.research-figure.has-animation');
  function stop(figure) {
    const img = figure.querySelector('img');
    const button = figure.querySelector('.animation-toggle');
    img.src = img.dataset.still;
    button.textContent = 'Play animation';
    button.setAttribute('aria-pressed', 'false');
  }
  figures.forEach((figure) => {
    const img = figure.querySelector('img');
    const button = figure.querySelector('.animation-toggle');
    button.hidden = false;
    button.addEventListener('click', () => {
      if (button.getAttribute('aria-pressed') === 'true') {
        stop(figure);
      } else {
        img.src = img.dataset.animation;
        button.textContent = 'Stop animation';
        button.setAttribute('aria-pressed', 'true');
      }
    });
  });
  motion.addEventListener('change', (event) => {
    if (event.matches) figures.forEach(stop);
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) figures.forEach(stop);
  });
})();
