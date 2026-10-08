import Headroom from 'js/headroom';

document.addEventListener('DOMContentLoaded', function() {
  // Older page templates do not assign an id to their main landmark.
  const main = document.querySelector('main');
  const skipLink = document.querySelector('.skip-link');
  if (main && skipLink) {
    if (!main.id) main.id = 'main-content';
    main.setAttribute('tabindex', '-1');
    skipLink.href = '#' + main.id;
    skipLink.hidden = false;
  }

  const Header = document.querySelector('.site-header');
  if (!Header || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const headroom = new Headroom(Header, {
    offset: 0,
    tolerance: { up: 5, down: 8 },
    classes: {
      initial: "header--fixed",
      top: "top",
      notTop: "not-top"
    }
  });
  headroom.init();
});
