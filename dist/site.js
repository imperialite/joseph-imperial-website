document.querySelectorAll('[data-filter]').forEach(button => {
  button.addEventListener('click', () => filterPublications(button.dataset.filter));
});

function filterPublications(topic) {
  let visible = 0;
  document.querySelectorAll('.paper').forEach(paper => {
    paper.hidden = topic !== 'all' && paper.dataset.topic !== topic;
    if (!paper.hidden) visible++;
  });
  document.querySelectorAll('[data-filter]').forEach(button => {
    const active = button.dataset.filter === topic;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  document.querySelector('.publication-count').textContent = `${visible} selected publications`;
}

document.querySelectorAll('[data-research-filter]').forEach(link => {
  link.addEventListener('click', () => filterPublications(link.dataset.researchFilter));
});

// Keep the current section visible in the navigation without scroll handlers.
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        document.querySelectorAll('.site-header nav a').forEach(link => {
          if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      }
    });
  }, { rootMargin: '-15% 0px -60% 0px' });
  document.querySelectorAll('#research, #publications, #about, #contact').forEach(section => observer.observe(section));
}
