searchInput.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        searchInput.value = '';
        searchInput.dispatchEvent(new Event('input')); // trigger search clear
    }
});