document.addEventListener('DOMContentLoaded', function () {
    const acceptButtons = document.querySelectorAll('.accept-button');
    const rejectButtons = document.querySelectorAll('.reject-button');
    const selectElements = document.querySelectorAll('select');

    selectElements.forEach(select => {
        select.addEventListener('change', function (event) {
            const acceptButton = select.parentElement.parentElement.querySelector('.accept-button');
            acceptButton.disabled = select.value === '';
        });
        select.dispatchEvent(new Event('change'));
    });

    const handleButtonClick = async (event, action) => {
        const button = event.target;
        const selectId = button.parentElement.parentElement.querySelector('select').value;
        const notificationType = button.dataset.notificationType;
        const notificationId = button.dataset.notificationId;
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

        if (!['Inscription', 'Reactivation'].includes(notificationType)) {
            alert(`Impossible de procéder à l'action demandée, la page va être rechargée.`);
            return window.location.reload();
        }

        try {
            button.disabled = true;
            button.parentElement.lastElementChild === button ? button.parentElement.firstElementChild.disabled = true : button.parentElement.lastElementChild.disabled = true;
            button.innerHTML = `${action} en cours...`;
            const response = await sendRequest(`/notifications/${notificationId}/${action}`, 'POST', csrfToken, { 'role_id': selectId });

            if (response.status !== 200) {
                throw new Error((await response.json()).error);
            }

            let json = await response.json();
            createFlashMessage(json.message, notificationId, action);
            button.parentElement.parentElement.parentElement.parentElement.remove();
        } catch (error) {
            createFlashMessage(error.message, notificationId, 'error');
            button.disabled = false;
            button.parentElement.lastElementChild === button ? button.parentElement.firstElementChild.disabled = false : button.parentElement.lastElementChild.disabled = false;
            button.innerHTML = action === 'accept' ? 'Accepter' : 'Rejeter';
        }
    };

    acceptButtons.forEach(button => {
        button.addEventListener('click', event => handleButtonClick(event, 'accept'));
    });

    rejectButtons.forEach(button => {
        button.addEventListener('click', event => handleButtonClick(event, 'reject'));
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

function createFlashMessage(message, notificationId, type) {
    const flash = document.createElement('div');
    flash.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible mt-4`;
    const button = document.createElement('button');
    button.type = "button";
    button.className = "btn-close";
    button.setAttribute('data-bs-dismiss', 'alert');
    button.setAttribute('data-notification-id', notificationId);
    button.addEventListener('click', function () {
        this.parentElement.remove();
    });
    flash.appendChild(button);
    const text = document.createTextNode(message);
    flash.appendChild(text);
    document.querySelector('.flash').appendChild(flash);
}