import { previewAfterRender } from './preview.js';
import { baseAfterRender } from './base.js';

document.addEventListener('DOMContentLoaded', function () {
    let csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    let accordionStates = {};

    function afterRender() {
        let favs = document.querySelectorAll('.favori');
        favs.forEach(function (fav) {
            let id = fav.id;
            let isFav = fav.getAttribute('is-fav');
            let etoile = document.getElementById("fav-" + id);
            if (isFav === "True") {
                fav.className = "favori-true";
            }
            else {
                fav.className = "favori-false";
                etoile.className = "fa-regular fa-star fa-lg me-2";
            }
            fav.addEventListener('click', function (event) {
                event.preventDefault();
                if (fav.className === "favori-true") {
                    fetch("favori/" + id, {
                        method: "DELETE",
                        headers: {
                            "Content-Type": "application/json",
                            'X-CSRFToken': csrfToken
                        }
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === "ok") {
                                fav.className = "favori-false";
                                etoile.className = "fa-regular fa-star fa-lg me-2";
                            }
                            else {
                                alert("Erreur lors de la suppression du favori");
                            }
                        });
                }
                else {
                    fetch("favori/" + id, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            'X-CSRFToken': csrfToken
                        }
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === "ok") {
                                fav.className = "favori-true";
                                etoile.className = "fa-solid fa-star fa-lg me-2";
                            }
                            else {
                                alert("Erreur lors de l'ajout du favori");
                            }
                        });
                }
            });
        });


        let accordions = document.querySelectorAll('.accordion-collapse');
        accordions.forEach(
            accordion => {
                accordion.addEventListener('show.bs.collapse', function (event) {
                    event.stopPropagation();
                    let id = accordion.id;
                    accordionStates[id] = true;
                });

                accordion.addEventListener('hide.bs.collapse', function (event) {
                    event.stopPropagation();
                    let id = accordion.id;
                    accordionStates[id] = false;
                });
            }
        )


        let desktops = document.querySelectorAll('.desktop');
        let deskList = JSON.parse(localStorage.getItem('desktop'));
        if (deskList === null) {
            deskList = [];
            localStorage.setItem('desktop', JSON.stringify(deskList));
        }

        desktops.forEach(
            desktop => {
                let fileId = desktop.id;
                let deskBtn = document.getElementById("desk-" + fileId); 
                if (deskList.includes(fileId)) {
                    desktop.className = "desktop-true";
                    deskBtn.className = "fa-regular fa-square-minus fa-lg";
                }
                else {
                    desktop.className = "desktop-false";
                }
                desktop.addEventListener('click', function (event) {
                    event.preventDefault();
                    let newDeskList = JSON.parse(localStorage.getItem('desktop'));
                    if (desktop.className === "desktop-true") {
                        newDeskList = newDeskList.filter(file => file !== fileId);
                        localStorage.setItem('desktop', JSON.stringify(newDeskList));
                        desktop.className = "desktop-false";
                        deskBtn.className = "fa-regular fa-square-plus fa-lg";
                    }
                    else {
                        newDeskList.push(fileId);
                        localStorage.setItem('desktop', JSON.stringify(newDeskList));
                        desktop.className = "desktop-true";
                        deskBtn.className = "fa-regular fa-square-minus fa-lg";
                    }
                    baseAfterRender(newDeskList.length);
                });
            }
        );
    }

    afterRender();

    let btn_and = document.getElementById("btn_and");
    let btn_or = document.getElementById("btn_or");
    let search_bar = document.getElementById("search-bar");

    btn_and.addEventListener('click', function () {
        search_bar.value += " & ";
    });

    btn_or.addEventListener('click', function () {
        search_bar.value += " | "
    });


    function renderFolder(folder, isOpen) {
        let expanded = isOpen ? 'true' : 'false';
        let collapsed = isOpen ? '' : 'collapsed';
        let show = isOpen ? 'show' : '';
    
        let html = `
        <div class="accordion-item" style="background-color: ${folder.color}; border: 1px solid black;">
            <h2 class="accordion-header" id="heading${folder.id}">
                <button class="accordion-button ${collapsed}" type="button" data-bs-toggle="collapse"
                    data-bs-target="#collapse${folder.id}" aria-expanded="${expanded}" aria-controls="collapse${folder.id}"
                    style="background-color: ${folder.color};">
                    <div class="d-flex w-100 align-items-center justify-content-between">
                        <div class="me-2 d-flex align-items-center">
                            <div class="d-flex">
                                <div class="me-2">
                                    <i class="fas fa-folder"></i>
                                </div>
                                <div>
                                    ${folder.name}
                                </div>
                            </div>
                            <div class="d-flex me-2" style="margin-left: 1rem;">
                                <div class="me-2">
                                    <i class="fas fa-file"></i>
                                </div>
                                <div>
                                    ${folder.files.length}
                                </div>
                            </div>
                        </div>
                    </div>
                </button>
            </h2>
            <div id="collapse${folder.id}" class="accordion-collapse collapse ${show}" aria-labelledby="heading${folder.id}"
                data-bs-parent="#accordion${folder.id}">
                <div class="accordion-body">
                    <div class="accordion" id="subfolderAccordion${folder.id}">
                    ${folder.subfolder.map(subfolder => {
                        let isOpen = accordionStates[`collapse${subfolder.id}`] || false;
                        return renderFolder(subfolder, isOpen);
                    }).join('')}
                    </div>
                    <div class="accordion" id="fichierAccordion${folder.id}"
                    style="height: 50vh; overflow: auto;">
                        ${folder.files.map(file => `
                            <div class="card mt-1 mb-1" style="height: 5vh" id="file-${file.id}">
                                <div class="card-body">
                                    <div class="d-flex me-2 w-100 justify-content-between align-items-baseline" style="cursor: pointer;">
                                        <div class="me-2 d-flex" style="flex-basis: -moz-available;" id="file" data-file="${file.id}" data-folder="${folder.id}" data-type="${file.extension}">
                                            <div class="me-2">
                                                <i class="fas fa-file"></i>
                                            </div>
                                            <div>
                                                <p class="mb-0">${file.title}</p>
                                            </div>
                                        </div>
                                        <div class="me-2 d-flex">
                                            <a href="/dossier/${folder.id}/fichier/${file.id}?as_attachment=true" style="display: inherit;">
                                                <i class="fa fa-download me-2" aria-hidden="true" style="cursor: pointer;" data-file="${file.id}" data-folder="${folder.id}"></i>
                                            </a>
                                            <a href="#" id="${file.id}" class="favori" is-fav="${file.favori}">
                                                <i class="fa-solid fa-star fa-lg" style="color: #FFD43B;"
                                                    id="fav-${file.id}"></i>
                                            </a>
                                            <a href="#" id="${file.id}" class="desktop">
                                                <i class="fa-regular fa-square-plus fa-lg" id="desk-${file.id}"></i>
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
        `;
        return html;
    }

    const socket = io.connect('/search');

    let searchBar = document.getElementById("search-bar");
    let searchButton = document.getElementById("search_btn");

    searchButton.addEventListener('click', function (event) {
        event.preventDefault(); 
    });

    searchBar.addEventListener('input', function () {
        socket.emit('search_files', { query: searchBar.value });
    });

    socket.on('search_results', function (data) {
        let accordion = document.getElementById("folderAccordion");
        accordion.innerHTML = data.map(folder => {
            let isOpen = accordionStates[`collapse${folder.id}`] || false;
            return renderFolder(folder, isOpen);
        }).join('');

        afterRender();
        previewAfterRender();
    });
    

});