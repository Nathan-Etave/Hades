let dossiers = document.querySelectorAll('.dossier');
let container = document.querySelector('.administration-container');
let dossier_placeholder = document.querySelector('.dossier-placeholder');
let target_dossier
let scope_dossier

for (let dossier of dossiers) {
    dossier.addEventListener('dragstart', dragStart);
    dossier.addEventListener('dragend', dragEnd);
    dossier.addEventListener('dragenter', dragEnter);
    dossier.addEventListener('touchstart', touchStart);
    dossier.addEventListener('touchend', touchEnd);
    dossier.addEventListener('touchmove', touchMove);
}

function dragStart(event) {
    target_dossier = event.target;
    target_dossier.classList.add('onDrag');
}

function dragEnd(event) {
    target_dossier.classList.remove('onDrag');
}

function dragEnter(event) {
    event.stopPropagation();
    let referenceNode = event.target;
    while (referenceNode.parentNode !== container) {
        referenceNode = referenceNode.parentNode;
    }
    container.insertBefore(target_dossier, referenceNode);
}

function touchStart(event) {
    defineScope(dossiers);
    target_dossier = event.target;
    target_dossier.classList.add('onDrag');
    dossier_placeholder.classList.remove('hidden');
    dossier_placeholder.style.top = event.changedTouches[0].clientY + 'px';
    dossier_placeholder.style.left = event.changedTouches[0].clientX + 'px';
    dossier_placeholder.innerText = event.target.innerText;
}

function touchEnd(event) {
    target_dossier.classList.remove('onDrag');
    dossier_placeholder.classList.add('hidden');
}

function touchMove(event) {
    dossier_placeholder.style.top = event.changedTouches[0].clientY + 'px';
    dossier_placeholder.style.left = event.changedTouches[0].clientX + 'px';
    hitTest(event.changedTouches[0]);
}

function hitTest(touch) {
    for (let dossier of dossiers) {
        let rect = dossier.getBoundingClientRect();
        if (touch.clientX > rect.left && touch.clientX < rect.right && touch.clientY > rect.top && touch.clientY < rect.bottom) {
            if (dossier !== target_dossier) {
                container.insertBefore(target_dossier, dossier);
            }
        }
    }
}

function defineScope(dossiers) {
    scope_dossier = [];
    for (let dossier of dossiers) {
        let new_dossier = {};
        new_dossier.target = dossier;
        new_dossier.startX = dossier.offsetLeft;
        new_dossier.startY = dossier.offsetTop;
        new_dossier.endX = dossier.offsetLeft + dossier.offsetWidth;
        new_dossier.endY = dossier.offsetTop + dossier.offsetHeight;
        scope_dossier.push(new_dossier);
    }
}

let dossier_name = document.querySelectorAll('.dossier > div > span:first-child');
for (let dossier of dossier_name) {
    dossier.addEventListener('input', function(event) {
        fetch('/administration/dossier/' + event.target.parentElement.querySelector('span:last-child').innerText, {
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'PUT',
            body: JSON.stringify({nom: event.target.innerText})
        });
    });
}

let fichier_input = document.querySelectorAll('.fichier-input');
let total_fichier = 0;
let upload_fichier = 0;
for (let input of fichier_input) {
    input.addEventListener('change', async function(event) {
        let dossier_id = input.parentElement.parentElement.parentElement.parentElement.querySelector('span:last-child').innerText;
        let files = input.files;
        total_fichier += files.length;
        for (let file of files) {
            await new Promise((resolve, reject) => {
                let reader = new FileReader();
                reader.onload = async function(e) {
                    let progress_bar = document.getElementById('progress-bar');
                    progress_bar.innerHTML = upload_fichier + '/' + total_fichier;
                    let response = await fetch('/administration/dossier/' + dossier_id + '/fichier', {
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        method: 'POST',
                        body: JSON.stringify({
                            nom: file.name,
                            data: e.target.result
                        })
                    });
                    let status = await response.status;
                    if (status === 200) {
                        upload_fichier++;
                        progress_bar.style.width = (upload_fichier / total_fichier) * 100 + '%';
                        progress_bar.innerHTML = upload_fichier + '/' + total_fichier;
                    }
                    resolve();
                }
                reader.readAsDataURL(file);
            });
        }
        input.parentElement.parentElement.reset();
    });
}