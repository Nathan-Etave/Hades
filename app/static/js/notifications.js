document.addEventListener('DOMContentLoaded', function () {
    let acceptButtons = document.querySelectorAll('.accept-button');
    let rejectButtons = document.querySelectorAll('.reject-button');
    let select = document.querySelectorAll('select');
    // isFetching implique que les boutons accepter et rejeter soit désactivés pendant la requête, il
    // faut régler ce problème en utilisant un flash (cf erreur mail) pour afficher un message disant
    // que telle chose est terminée. (Plus de boutons désactivés (seulement le bouton cliqué et son opposé))
    // Liste de flash avec un timer de 5sec ? S'affiche un a un ? Ou un seul flash qui s'actualise ?
    let isFetching = false;

    select.forEach(function (select) {
        select.addEventListener('change', function (event) {
            if (isFetching) {
                return;
            }
            if (select.value != '') {
                select.parentElement.parentElement.querySelector('.accept-button').disabled = false;
            }
            else {
                select.parentElement.parentElement.querySelector('.accept-button').disabled = true;
            }
        });
        select.dispatchEvent(new Event('change'));
    });

    acceptButtons.forEach(button => {
        button.addEventListener('click', async function (event) {
            let selectId = event.target.parentElement.parentElement.querySelector('select').value;
            let notificationType = event.target.dataset.notificationType;
            let notificationId = event.target.dataset.notificationId;
            let csrfToken = document.querySelector('meta[name="csrf-token"]').content;

            if (selectId === '') {
                return alert('Veuillez sélectionner un rôle avant de valider.');
            }

            if (!['Inscription', 'Reactivation'].includes(notificationType)) {
                alert('Erreur lors de la validation.');
                return window.location.reload();
            }

            try {
                isFetching = true;
                acceptButtons.forEach(button => button.disabled = true);
                rejectButtons.forEach(button => button.disabled = true);
                event.target.innerHTML = 'Validation en cours...';
                let response = await sendRequest(`/notifications/${notificationId}/accept`, 'POST', csrfToken, {
                    'role_id': selectId
                });
            
                if (response.status === 200) {
                    isFetching = false;
                    alert(notificationType === 'Inscription' ? 'Validation effectuée avec succès.' : 'Réactivation effectuée avec succès.');
                    window.location.reload();
                }
                else {
                    isFetching = false;
                    let data = await response.json();
                    throw new Error(data.error);
                }
            } catch (error) {
                let flash = `<div class="alert alert-danger alert-dismissible mt-4">
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    ${error.message}
                    </div>`
                document.querySelector('.flash').innerHTML = flash;
                document.querySelector('.flash').querySelector('.btn-close').addEventListener('click', function () {
                    document.querySelector('.flash').innerHTML = '';
                });
                acceptButtons.forEach(button => selectId === '' ? button.disabled = true : button.disabled = false);
                rejectButtons.forEach(button => button.disabled = false);
                event.target.innerHTML = 'Accepter';
            }
        });
    });

    rejectButtons.forEach(button => {
        button.addEventListener('click', async function (event) {
            let notificationId = event.target.dataset.notificationId;
            let notificationType = event.target.dataset.notificationType;
            let selectId = event.target.parentElement.parentElement.querySelector('select').value;
            let csrfToken = document.querySelector('meta[name="csrf-token"]').content;

            if (!['Inscription', 'Reactivation'].includes(notificationType)) {
                alert('Erreur lors du rejet.');
                return window.location.reload();
            }

            try {
                isFetching = true;
                acceptButtons.forEach(button => button.disabled = true);
                rejectButtons.forEach(button => button.disabled = true);
                event.target.innerHTML = 'Rejet en cours...';
                let response = await sendRequest(`/notifications/${notificationId}/reject`, 'POST', csrfToken);
            
                if (response.status === 200) {
                    isFetching = false;
                    alert(notificationType === 'Inscription' ? 'Rejet effectué avec succès.' : 'Désactivation effectuée avec succès.');
                    window.location.reload();
                }
                else {
                    isFetching = false;
                    let data = await response.json();
                    throw new Error(data.error);
                }
            } catch (error) {
                let flash = `<div class="alert alert-danger alert-dismissible mt-4">
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    ${error.message}
                    </div>`
                document.querySelector('.flash').innerHTML = flash;
                document.querySelector('.flash').querySelector('.btn-close').addEventListener('click', function () {
                    document.querySelector('.flash').innerHTML = '';
                });
                acceptButtons.forEach(button => selectId === '' ? button.disabled = true : button.disabled = false);
                rejectButtons.forEach(button => button.disabled = false);
                event.target.innerHTML = 'Rejeter';
            }
        });
    });
});

async function sendRequest(url, method, csrfToken, body = null) {
    return await fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: body ? JSON.stringify(body) : null
    });
}