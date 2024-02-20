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

let dossier_name = document.querySelectorAll('.dossier > span:first-child');
for (let dossier of dossier_name) {
    dossier.addEventListener('input', function(event) {
        console.log(event.target.innerText);
        fetch('/administration/dossier/' + event.target.parentElement.querySelector('span:last-child').innerText, {
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'PUT',
            body: JSON.stringify({nom: event.target.innerText})
        });
    });
}