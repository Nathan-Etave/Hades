import { previewAfterRender } from "./preview.js";

document.addEventListener('DOMContentLoaded', function () {    
    const acceptButtons = document.querySelectorAll('.accept-button');
    const rejectButtons = document.querySelectorAll('.reject-button');
    const selectElements = document.querySelectorAll('select');

    previewAfterRender();

    selectElements.forEach(select => {
        select.addEventListener('change', function (event) {
            const acceptButton = select.parentElement.parentElement.querySelector('.accept-button');
            acceptButton.disabled = select.value === '';
        });
        select.dispatchEvent(new Event('change'));
    });

    const handleButtonClick = async (event, action) => {
        const button = event.target;
        let selectId = button.parentElement.parentElement.querySelector('select').value;
        const notificationType = button.dataset.notificationType;
        const notificationId = button.dataset.notificationId;
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

        button.parentElement.parentElement.querySelector('select').addEventListener('change', function (event) {
            selectId = event.target.value;
        });

        if (!["1", "2"].includes(notificationType)) {
            createAlertMessage('Impossible de procéder à l\'action demandée.', 'error', true);
            return window.location.reload();
        }

        try {
            button.disabled = true;
            button.parentElement.lastElementChild === button ? button.parentElement.firstElementChild.disabled = true : button.parentElement.lastElementChild.disabled = true;
            button.innerHTML = action === 'accept' ? 'Acceptation en cours...' : 'Rejet en cours...';
            const response = await sendRequest(`/notifications/${notificationId}/${action}`, 'POST', csrfToken, { 'role_id': selectId });

            if (response.status !== 200) {
                throw new Error((await response.json()).error);
            }

            let json = await response.json();
            createAlertMessage(json.message, action);
            button.parentElement.parentElement.parentElement.parentElement.remove();
        } catch (error) {
            createAlertMessage(error.message, 'error');
            if (button.parentElement.lastElementChild === button) {
                button.disabled = false;
                selectId == '' ? button.parentElement.firstElementChild.disabled = true : button.parentElement.firstElementChild.disabled = false;
            }
            else {
                selectId == '' ? button.disabled = true : button.disabled = false;
                button.parentElement.lastElementChild.disabled = false;
            }
            button.innerHTML = action === 'accept' ? 'Accepter' : 'Rejeter';
        }
    };

    acceptButtons.forEach(button => {
        button.addEventListener('click', event => handleButtonClick(event, 'accept'));
    });

    rejectButtons.forEach(button => {
        button.addEventListener('click', event => handleButtonClick(event, 'reject'));
    });

    const socket = io.connect('/notifications');
    const historyContainer = document.querySelector('#historyContainer');
    socket.on('file_processed', (data) => {
        let div = document.createElement('div');
        div.className = 'd-flex hover-underline file-text-notification';
        div.id = 'file';
        div.dataset.file = data.file.id_Fichier;
        div.dataset.folder = data.folder_id;
        div.dataset.type = data.file.extension_Fichier;
        div.dataset.name = data.filename;
        div.innerHTML = `
        <p style="font-size: 1.1rem;" class="file-text-notification">
            <span style="font-weight: bold; color: #007BFF;">[${data.file.date_Fichier}] </span>
            <span>Le fichier "<span class="file-notification" style="cursor: pointer; color: #0000ff;">${data.file.nom_Fichier}</span>" </span>
            <span>a été ${data.action === true ? 'réécrit' : 'ajouté'} dans le classeur "<span style="color: #ecb900;">${data.folder.nom_Dossier}</span>" par 
            <span style="color: #dc3545;">${data.user.nom_Utilisateur} ${data.user.prenom_Utilisateur}.</span>
            </span>
        </p>
        `;
        historyContainer.insertBefore(div, historyContainer.firstChild);
        previewAfterRender();
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

function createAlertMessage(message, type, confirm = false) {
    Swal.fire({
        icon: type === 'error' ? 'error' : 'success',
        title: type === 'error' ? 'Une erreur est survenue.' : 'Action effectuée avec succès.',
        text: message,
        position: 'top-end',
        showConfirmButton: confirm,
        timer: 2000,
        backdrop: false
    })


}