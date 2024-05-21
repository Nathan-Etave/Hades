//function import 
import { previewAfterRender } from './preview.js';
import { baseAfterRender } from './base.js';

document.addEventListener('DOMContentLoaded', function () {
    // Initilisation 
    let deskList = JSON.parse(localStorage.getItem('desktop'));
    if (deskList === null) {
        deskList = [];
        localStorage.setItem('desktop', JSON.stringify(deskList));
    }
    let csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    // Socket initialization
    const socket = io.connect('/file_handler');
    const userId = document.querySelector('meta[name="current-user"]').content;
    socket.on('connect', function () {
        socket.emit('join', { room: `user_${userId}` });
        // emit event to get files details
        socket.emit('get_files_details', { 'files': deskList });
    });

    // Handle the display of the desktop
    let currentFile = 0;
    let desktop = document.getElementById('deskSection');
    socket.on('files_details', function (data) {
        let modalFooter = document.querySelector('.nav-tabs');
        desktop.innerHTML = '';
        localStorage.setItem('desktop', JSON.stringify(data["files_id"]));
        baseAfterRender(data["files"].length);

        let deskFileNumber = 1;
        data["files"].forEach(function (file) {

            // Create the card
            let div = document.createElement('div');
            div.className = 'col-2';
            div.id = "div-file-" + file.id_Fichier;
            div.setAttribute('data-number', deskFileNumber);

            let card = document.createElement('div');
            card.className = 'card';
            card.style.height = '18rem';
            card.style.margin = '2rem 2rem';
            card.style.wordBreak = 'break-word';
            card.style.cursor = 'pointer';
            card.style.border = '3px solid #004F8A';

            let fileDiv = document.createElement('div');
            fileDiv.className = 'card-body d-flex flex-column file-' + deskFileNumber;
            fileDiv.setAttribute('data-file', file.id_Fichier);
            fileDiv.setAttribute('data-folder', file.id_Dossier);
            fileDiv.setAttribute('data-type', file.extension_Fichier);
            fileDiv.id = 'file';
            fileDiv.style.textAlign = 'center';
            fileDiv.innerHTML = `<div class="desktop-element">
                                    <i class="fa-regular fa-file fa-2xl" style="font-size: 6em; margin-bottom: 4rem; margin-top: 4rem"></i>
                                 </div>
                                 <div>
                                    <p class="card-title h5" style="font-size: 1.5em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">${file.nom_Fichier}<p>
                                 </div>
                                 <div class="desktop-element mt-auto d-flex justify-content-center">
                                    <a href="#" id="${file.id_Fichier}" class="favori" is-fav="${file.is_favorite}" onclick="event.stopPropagation();">
                                        <i class="fa-solid fa-star fa-lg me-2" style="color: #FFD43B;"
                                            id="fav-${file.id_Fichier}"></i>
                                    </a>
                                    <a href="#" id="${file.id_Fichier}" class="desktop-btn" onclick="event.stopPropagation();">
                                        <i class="fa-regular fa-square-minus fa-lg me-2" id="desk-${file.id_Fichier}"></i>
                                    </a>
                                    <a href="/classeur/${file.id_Dossier}/fichier/${file.id_Fichier}?as_attachment=true"
                                        style="display: inherit;">
                                        <i class="fa fa-download mt-1" aria-hidden="true" style="cursor: pointer;"
                                            data-file="${file.id_Fichier}" data-folder="${file.id_Dossier}"></i>
                                    </a>
                                 </div>`;

            // Add event on the card to change the current file and activate the corresponding nav
            fileDiv.addEventListener('click', function () {
                let fileNumber = parseInt(fileDiv.className.split('-')[4]);
                let nav = document.querySelector('.nav-' + fileNumber);
                nav.classList.add('active');
                currentFile = fileNumber;
            });

            card.appendChild(fileDiv);
            div.appendChild(card);
            desktop.appendChild(div);

            // Create the nav
            let fileNav = document.createElement('li');
            let fileNavText = document.createElement('p');
            fileNavText.className = 'nav-link nav-' + deskFileNumber;
            fileNavText.textContent = file.nom_Fichier;
            fileNavText.style.whiteSpace = 'nowrap';
            fileNavText.style.overflow = 'hidden';
            fileNavText.style.textOverflow = 'ellipsis';
            fileNav.appendChild(fileNavText);

            fileNav.className = 'file-nav nav-item';
            fileNav.setAttribute('file-number', deskFileNumber);
            fileNav.style.cursor = 'pointer';
            fileNav.style.width = 'auto';
            fileNav.style.maxWidth = '15vw';
            modalFooter.appendChild(fileNav);

            // Add event on the nav to change the current file and activate the corresponding card
            fileNav.addEventListener('click', function () {
                let fileNumber = fileNav.getAttribute('file-number');
                let card = document.querySelector('.file-' + fileNumber);
                let newNav = document.querySelector('.nav-' + fileNumber);
                let previousNav = document.querySelector('.nav-' + currentFile);
                newNav.classList.add('active');
                previousNav.classList.remove('active');
                currentFile = fileNumber;
                card.click();
            });

            deskFileNumber++;

        });

        // Hndle the favori button
        let favs = document.querySelectorAll('.favori');
        favs.forEach(function (fav) {
            let id = fav.id;
            let isFav = fav.getAttribute('is-fav');
            let etoile = document.getElementById("fav-" + id);
            if (isFav === "true") {
                fav.className = "favori-true";
            }
            else {
                fav.className = "favori-false";
                etoile.className = "fa-regular fa-star fa-lg me-2";
            }
            fav.addEventListener('click', function (event) {
                event.preventDefault();
                if (fav.className === "favori-true") {
                    fetch("/favori/" + id, {
                        method: "DELETE",
                        headers: {
                            "Content-Type": "application/json",
                            'X-CSRFToken': csrfToken
                        }
                    })
                        .then(response => response.json().then(data => ({ status: response.status, body: data })))
                        .then(data => {
                            if (data.status === 200) {
                                fav.className = "favori-false";
                                etoile.className = "fa-regular fa-star fa-lg me-2";
                            }
                            else {
                                createErrorAlertMessage('Erreur lors de la suppression du favori.', data.body);
                            }
                        });
                }
                else {
                    fetch("/favori/" + id, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            'X-CSRFToken': csrfToken
                        }
                    })
                        .then(response => response.json().then(data => ({ status: response.status, body: data })))
                        .then(data => {
                            if (data.status === 200) {
                                fav.className = "favori-true";
                                etoile.className = "fa-solid fa-star fa-lg me-2";
                            }
                            else {
                                createErrorAlertMessage('Erreur lors de l\'ajout du favori.', data.body);
                            }
                        });
                }
            });
        });

        // Handle the button to remove a file from the desktop
        let deskBtns = document.querySelectorAll('.desktop-btn');
        deskBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                let id = btn.id;
                let deskList = JSON.parse(localStorage.getItem('desktop'));
                let index = deskList.indexOf(id);
                if (index !== -1) {
                    deskList.splice(index, 1);
                }
                localStorage.setItem('desktop', JSON.stringify(deskList));
                window.location.reload();
            });
        });


        previewAfterRender();

    });


    // Handle the navigation with the keyboard
    window.addEventListener('keydown', function (event) {
        let nbFiles = document.querySelectorAll('#file').length;
        if (currentFile !== 0) {
            let nav = document.querySelector('.nav-' + currentFile);
            nav.classList.remove('active');
            if (event.key === 'ArrowRight') {
                currentFile++;
                if (currentFile > nbFiles) {
                    currentFile = 1;
                }
            } else if (event.key === 'ArrowLeft') {
                currentFile--;
                if (currentFile < 1) {
                    currentFile = nbFiles;
                }
            }
            let card = document.querySelector('.file-' + currentFile);
            card.click();
        }
    });

    // desactivate the current file nav when closing the preview
    let btnClose = document.querySelector('.btn-close');
    btnClose.addEventListener('click', function () {
        let nav = document.querySelector('.nav-' + currentFile);
        nav.classList.remove('active');
        currentFile = 0;
    });

    // Handle the clear button
    let btnClear = document.getElementById("clear");
    btnClear.addEventListener('click', function () {
        localStorage.setItem('desktop', JSON.stringify([]));
        desktop.innerHTML = '';
        baseAfterRender(0);
    });

    function createErrorAlertMessage(message, data) {
        Swal.fire({
            position: 'top-end',
            icon: 'error',
            title: message,
            text: data.error,
            showConfirmButton: false,
            timer: 2500,
            backdrop: false
        });
    }
});