const search = document.getElementById('publication-search');
const topic = document.getElementById('publication-topic');
if (search && topic) {
  document.querySelector('.publication-tools').hidden = false;
  const filter = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    document.querySelectorAll('.paper').forEach(paper => {
      const matches = (topic.value === 'all' || paper.dataset.topic === topic.value)
        && paper.textContent.toLocaleLowerCase().includes(query);
      paper.hidden = !matches;
      if (matches) count++;
    });
    document.querySelectorAll('.year-group').forEach(group => {
      group.hidden = !group.querySelector('.paper:not([hidden])');
    });
    const status = document.querySelector('.result-count');
    status.hidden = !query && topic.value === 'all';
    status.textContent = `${count} ${count === 1 ? 'publication' : 'publications'} found`;
    document.querySelector('.empty-state').hidden = count !== 0;
  };
  search.addEventListener('input', filter);
  topic.addEventListener('change', filter);
}
