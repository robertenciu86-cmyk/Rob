// Brendan gallery lightbox. Without JS the photos just open as full-size links.
(function () {
    var shots = document.querySelectorAll('.bz-shot');
    if (!shots.length || !window.HTMLDialogElement) return;
    var dialog = document.createElement('dialog');
    dialog.className = 'bz-lightbox';
    dialog.innerHTML = '<img alt=""><p></p><button type="button" aria-label="Close">×</button>';
    document.body.appendChild(dialog);
    var img = dialog.querySelector('img');
    var caption = dialog.querySelector('p');
    shots.forEach(function (shot) {
        shot.addEventListener('click', function (event) {
            event.preventDefault();
            img.src = shot.getAttribute('href');
            img.alt = shot.querySelector('img').alt;
            caption.textContent = shot.getAttribute('data-caption');
            dialog.showModal();
        });
    });
    dialog.addEventListener('click', function (event) {
        if (event.target !== img) dialog.close();
    });
})();
