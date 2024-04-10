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
    acceptButtons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            let selectId = event.target.parentElement.parentElement.querySelector('select').value;
            let notificationType = event.target.dataset.notificationType;
            let notificationId = event.target.dataset.notificationId;
            let csrfToken = document.querySelector('meta[name="csrf-token"]').content;
            let userId = event.target.dataset.userId;
            if (selectId == '') {
                alert('Veuillez sélectionner un rôle avant de valider.');
            }
            else if (userId === '' || isNaN(userId) || !['Inscription', 'Reactivation'].includes(notificationType)) {
                alert('Erreur lors de la validation.');
                window.location.reload();
            }
            else {
                if (notificationType === 'Inscription') {
                    fetch(`/api/utilisateur/${userId}`, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({
                            role: selectId,
                            actif: true
                        })
                    })
                        .then(response => response.status)
                        .then(status => {
                            if (status === 200) {
                                fetch(`/api/notification/${notificationId}`, {
                                    method: 'DELETE',
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'X-CSRFToken': csrfToken
                                    }
                                })
                                    .then(response => response.status)
                                    .then(status => {
                                        if (status === 200) {
                                            alert('Validation effectuée avec succès.');
                                            window.location.reload();
                                        }
                                        else {
                                            alert('Erreur lors de la validation.');
                                            window.location.reload();
                                        }
                                    });
                            }
                            else if (status === 403 || status === 404) {
                                alert('Erreur lors de la validation.');
                                window.location.reload();
                            }
                        }
                        );
                }
            }
        });
    });
    rejectButtons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            let notificationType = event.target.dataset.notificationType;
            let userId = event.target.dataset.userId;
        });
    });
});
