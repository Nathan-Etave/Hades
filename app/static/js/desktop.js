//function import 
import { previewAfterRender } from './preview.js';
import { baseAfterRender } from './base.js';

document.addEventListener('DOMContentLoaded', function () {
    // Initilisation 
    document.body.style.overflowX = 'hidden';
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
            div.className = mobileCheck() ? 'col-6' : 'col-3';
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
            fileDiv.style.overflow = 'hidden';
            fileDiv.id = 'file';
            fileDiv.style.textAlign = 'center';
            fileDiv.innerHTML = `<div class="desktop-element">
                                    <img class="desktop-screenshot" src="/classeur/${file.id_Dossier}/fichier/${file.id_Fichier}?as_screenshot=true" class="card-img-top" style="height: 10rem; width: auto; object-fit: contain; max-width: 100%; max-height: 100%;">
                                 </div>
                                 <div>
                                    <p class="card-title h5" style="font-size: 1.5em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">${file.nom_Fichier}<p>
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

            fileNav.className = 'file-nav nav-items';
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

    function mobileCheck() {
        let check = false;
        (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor||window.opera);
        return check;
    };
});