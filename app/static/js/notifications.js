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
            alert(`Impossible de procéder à l'action demandée, la page va être rechargée.`);
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
            createFlashMessage(json.message, notificationId, action);
            button.parentElement.parentElement.parentElement.parentElement.remove();
        } catch (error) {
            createFlashMessage(error.message, notificationId, 'error');
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
    setTimeout(() => flash.remove(), 5000);
}