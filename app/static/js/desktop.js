import { previewAfterRender } from './preview.js';

document.addEventListener('DOMContentLoaded', function () {
    let deskList = JSON.parse(localStorage.getItem('desktop'));
    if (deskList === null) {
        deskList = [];
        localStorage.setItem('desktop', JSON.stringify(deskList));
    }

    const socket = io.connect('/file_handler');

    socket.emit('get_files_details', { 'files': deskList });

    let currentFile = 1;

    socket.on('files_details', function (data) {
        let desktop = document.getElementById('desk-section');
        let modalFooter = document.querySelector('.nav-tabs');
        desktop.innerHTML = '';

        let deskFileNumber = 1;
        data.forEach(function (file) {
            let div = document.createElement('div');
            div.className = 'col-2';

            let card = document.createElement('div');
            card.className = 'card';
            card.style.height = '18rem';
            card.style.margin = '2rem 2rem';
            card.style.wordBreak = 'break-word';
            card.style.cursor = 'pointer';
            card.style.border = '3px solid #004F8A';

            let fileDiv = document.createElement('div');
            fileDiv.className = 'card-body file-' + deskFileNumber;
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
                                 </div>`;

            fileDiv.addEventListener('click', function () {
                let fileNumber = parseInt(fileDiv.className.split(' ')[1].split('-')[1], 10);
                let nav = document.querySelector('.nav-' + fileNumber);
                nav.classList.add('active');
                currentFile = fileNumber;
            });

            card.appendChild(fileDiv);
            div.appendChild(card);
            desktop.appendChild(div);


            let fileNav = document.createElement('li');
            let fileNavText = document.createElement('p');
            fileNavText.className = 'nav-link nav-'+deskFileNumber;
            fileNavText.textContent = file.nom_Fichier;
            fileNavText.style.whiteSpace = 'nowrap';
            fileNavText.style.overflow = 'hidden';
            fileNavText.style.textOverflow = 'ellipsis';
            fileNav.appendChild(fileNavText);

            fileNav.className = 'file-nav nav-item';
            fileNav.setAttribute('file-number', deskFileNumber);
            fileNav.style.cursor = 'pointer';
            fileNav.style.width = '15vw';
            modalFooter.appendChild(fileNav);

            fileNav.addEventListener('click', function() {
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
        previewAfterRender();

    });


    window.addEventListener('keydown', function (event) {
        let nbFiles = document.querySelectorAll('#file').length;
        let nav = document.querySelector('.nav-' + currentFile);
        nav.classList.remove('active');
        if (currentFile !== 0) {
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

    let btnClose = document.querySelector('.btn-close');
    btnClose.addEventListener('click', function () {
        let nav = document.querySelector('.nav-' + currentFile);
        nav.classList.remove('active');
        currentFile = 0;
    });

});