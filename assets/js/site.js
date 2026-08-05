(() => {
  const menuButton = document.querySelector('.menu-button');
  const navigation = document.querySelector('#site-navigation');
  if (menuButton && navigation) {
    menuButton.addEventListener('click', () => {
      const open = navigation.classList.toggle('open');
      menuButton.setAttribute('aria-expanded', String(open));
      const label = menuButton.querySelector('.sr-only');
      if (label) label.textContent = open ? 'Close navigation' : 'Open navigation';
    });
    navigation.addEventListener('click', (event) => {
      if (event.target.closest('a') && navigation.classList.contains('open')) {
        navigation.classList.remove('open');
        menuButton.setAttribute('aria-expanded', 'false');
      }
    });
  }

  document.querySelectorAll('[data-copy-target]').forEach((button) => {
    button.addEventListener('click', async () => {
      const target = document.querySelector(button.dataset.copyTarget);
      const status = button.parentElement.querySelector('.copy-status');
      if (!target) return;
      try {
        await navigator.clipboard.writeText(target.textContent.trim());
        if (status) status.textContent = 'Citation copied.';
      } catch (error) {
        if (status) status.textContent = 'Copy failed. Select the citation text manually.';
      }
    });
  });
})();
