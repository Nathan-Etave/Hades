document.addEventListener('DOMContentLoaded', function () {
    let acceptButtons = document.querySelectorAll('.accept-button');
    let rejectButtons = document.querySelectorAll('.reject-button');
    let select = document.querySelectorAll('select');

    select.forEach(function (select) {
        select.addEventListener('change', function (event) {
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
                let response = await sendRequest(`/notifications/${notificationId}/accept`, 'POST', csrfToken, {
                    'role_id': selectId
                });

                if (response.status === 200) {
                    alert(notificationType === 'Inscription' ? 'Validation effectuée avec succès.' : 'Réactivation effectuée avec succès.');
                    window.location.reload();
                }
                else {
                    throw new Error();
                }
            } catch (error) {
                console.error(error);
                alert('Erreur lors de la validation.');
                window.location.reload();
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