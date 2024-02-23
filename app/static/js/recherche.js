let interval_check = setInterval(checkStatus, 500);
function checkStatus() {
    fetch('/status/' + job_id)
        .then(response => response.json())
        .then(data => {
            let summaries_id = document.querySelectorAll('summary > span');
            summaries_id = new Set(Array.from(summaries_id).map(span => span.id));
            let all_loaded = true;
            let dossiers = Object.values(data['job']).sort((a, b) => a['priorite'] - b['priorite']);
            for (let dossier of dossiers) {
                if (dossier['status'] && !summaries_id.has(dossier['id'].toString())) {
                    let details = createDetails(dossier);
                    document.querySelector('.recherche-container').insertAdjacentHTML('beforeend', details);
                    details = document.querySelector('.recherche-container').lastElementChild;
                    for (let fichier in dossier['fichiers']) {
                        let div = createDiv(dossier['fichiers'][fichier], dossier['couleur']);
                        details.insertAdjacentHTML('beforeend', div);
                    }
                }
                all_loaded = all_loaded && dossier['status'];
            }
            if (all_loaded) {
                clearInterval(interval_check);
            }
        }
    );
}

function createDetails(dossier) {
    return /*html*/`
        <details open id="favoris">
            <summary style="background-color: ${dossier['couleur']}; font-size: 2rem;">
                ${dossier['nom']} (${dossier['fichiers'].length})
                <span id="${dossier['id']}" style="display: none;">
            </summary>
        </details>
        `;
}

function createDiv(fichier, couleur) {
    return /*html*/`
        <div class="fichier" id="${fichier['id']}" style="background-color: ${couleur}">
            <a class="bouton_fichier" id="${fichier['id']}">${fichier['nom']}</a>
            <div class="bob">
                <img src="static/img/telechargement.png" alt="telechargement" class="telechargement" id="${fichier['id']}">
                <img src="static/img/moins.png" alt="multiview" class="multiview" id="id ${fichier['id']}">
                <img src="static/img/etoile_pleine.png" alt="etoile" class="etoile" id="${fichier['id']}">
            </div>
            <span id="type_${fichier['id']}" style="display: none;">${fichier['extension']}</span>
        </div>
        `;
}