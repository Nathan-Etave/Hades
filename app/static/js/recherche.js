let interval_check = setInterval(checkStatus, 500);
function checkStatus() {
    fetch('/status/' + job_id)
        .then(response => response.json())
        .then(data => {
            let summaries_id = document.querySelectorAll('summary > span');
            summaries_id = new Set(Array.from(summaries_id).map(span => span.id));
            let all_loaded = true;
            for (let dossier in data['job']) {
                if (data['job'][dossier]['status'] && !summaries_id.has(data['job'][dossier]['id'].toString())) {
                    let details = createDetails(data['job'][dossier]);
                    document.querySelector('.recherche-container').insertAdjacentHTML('beforeend', details);
                    details = document.querySelector('.recherche-container').lastElementChild;
                    for (let fichier in data['job'][dossier]['fichiers']) {
                        let div = createDiv(data['job'][dossier]['fichiers'][fichier]);
                        details.insertAdjacentHTML('beforeend', div);
                    }
                }
                all_loaded = all_loaded && data['job'][dossier]['status'];
            }
            if (all_loaded) {
                clearInterval(interval_check);
            }
        }
    );
}

function createDetails(dossier) {
    return /*html*/`
        <details open>
            <summary style="background-color: ${dossier['couleur']}; font-size: 2rem;">
                ${dossier['nom']}
                <span id="${dossier['id']}" style="display: none;">
            </summary>
        </details>
        `;
}

function createDiv(fichier) {
    return /*html*/`
        <div class="fichier">
            ${fichier['nom']}
            <span id="${fichier['id']}" style="display: none;">
        </div>
        `;
}