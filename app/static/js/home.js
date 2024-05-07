import { baseAfterRender } from './base.js';
import { previewAfterRender } from './preview.js';

document.addEventListener('DOMContentLoaded', function () {

    let btn_and = document.getElementById("btn_and");
    let btn_or = document.getElementById("btn_or");
    let search_bar = document.getElementById("search-bar");
    let csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    // Add search operator in the search bar
    btn_and.addEventListener('click', function () {
        search_bar.value += " & ";
    });
    btn_or.addEventListener('click', function () {
        search_bar.value += " | "
    });

    // Function to apply the JS after the render of the panel 
    function panelAfterRender() {
        // Handle favori in the side panel
        let favorites_btn = document.querySelectorAll(".favori-home");
        favorites_btn.forEach(function (btn) {
            btn.addEventListener('click', function () {
                let id = btn.id;
                let url = "/favori/" + id;
                fetch(url, {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                        'X-CSRFToken': csrfToken
                    }
                })
                    .then(response => response.json().then(data => ({ status: response.status, body: data })))
                    .then(data => {
                        if (data.status === 200) {
                            let div_fav = document.querySelector(".fav"+id);
                            div_fav.remove();
                            let favElement = document.getElementById("fav-" + id);
                            favElement.className = "fa-regular fa-star fa-lg me-2";
                        }
                        else {
                            createErrorAlertMessage("Erreur lors de la suppression du favori.", data.body);
                        }
                    });
            });
        });

        // Handle previous seartch terms in the side panel
        let search_tiles = document.querySelectorAll(".search_term");
        let search_btn = document.getElementById("search_btn");
        search_tiles.forEach(function (tile) {
            tile.addEventListener('click', function () {
                search_bar.value = tile.getAttribute("query");
                search_btn.click();
            });
        });
    }

    // Function to apply the JS to the desktop buton after the render
    function desktopAfterRender() {
        // Get the desktop list from the local storage
        let desktops = document.querySelectorAll('.desktop');
        let deskList = JSON.parse(localStorage.getItem('desktop'));
        if (deskList === null) {
            deskList = [];
            localStorage.setItem('desktop', JSON.stringify(deskList));
        }

        // Handle the desktop add/remove button from the side panel and the search results
        desktops.forEach(
            desktop => {
                let fileId = desktop.id;
                let deskBtn = document.getElementById("desk-" + fileId);
                let deskHomeBtn = document.getElementById("desk-home-" + fileId); 
                if (deskList.includes(fileId)) {
                    desktop.className = "desktop-true";
                    deskBtn.className = "fa-regular fa-square-minus fa-lg";
                    if (deskHomeBtn !== null) {
                        deskHomeBtn.className = "fa-regular fa-square-minus fa-lg";
                    }
                }
                else {
                    desktop.className = "desktop-false";
                }
                desktop.addEventListener('click', function (event) {
                    event.preventDefault();
                    let newDeskList = JSON.parse(localStorage.getItem('desktop'));
                    let deskHomeBtn = document.getElementById("desk-home-" + fileId);
                    if (desktop.className === "desktop-true") {
                        newDeskList = newDeskList.filter(file => file !== fileId);
                        localStorage.setItem('desktop', JSON.stringify(newDeskList));
                        desktop.className = "desktop-false";
                        deskBtn.className = "fa-regular fa-square-plus fa-lg";
                        if (deskHomeBtn !== null) {
                            deskHomeBtn.className = "fa-regular fa-square-plus fa-lg";
                        }
                    }
                    else {
                        newDeskList.push(fileId);
                        localStorage.setItem('desktop', JSON.stringify(newDeskList));
                        desktop.className = "desktop-true";
                        deskBtn.className = "fa-regular fa-square-minus fa-lg";
                        if (deskHomeBtn !== null) {
                            deskHomeBtn.className = "fa-regular fa-square-minus fa-lg";
                        }
                    }
                    baseAfterRender(newDeskList.length);
                });
            }
        );
    }

    //apply the JS the first time
    panelAfterRender();
    desktopAfterRender();

    // Handle favori in the search results
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
                        .then(response => response.json().then(data => ({ status: response.status, body: data })))
                        .then(data => {
                            if (data.status === 200) {
                                fav.className = "favori-false";
                                etoile.className = "fa-regular fa-star fa-lg me-2";
                                let favTile = document.querySelector(".fav" + id);
                                if (favTile !== null) {
                                    favTile.remove();
                                }
                            }
                            else {
                                createErrorAlertMessage("Erreur lors de la suppression du favori.", data.body);
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
                        .then(response => response.json().then(data => ({ status: response.status, body: data })))
                        .then(data => {
                            if (data.status === 200) {
                                fav.className = "favori-true";
                                etoile.className = "fa-solid fa-star fa-lg me-2";
                                let elem = fav.parentElement.parentElement.querySelector("#file");
                                displayFav(elem.getAttribute("data-file"), elem.getAttribute("data-name"), elem.getAttribute("data-folder"), elem.getAttribute("data-type"));
                            }
                            else {
                                createErrorAlertMessage("Erreur lors de l'ajout du favori.", data.body);
                            }
                        });
                }
            });
        });

    // Function to display a new favorite in the side panel
    function displayFav(id, name, id_folder, extension) {
        let div = document.createElement('div');
    
        div.innerHTML = `
            <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center fav${id}" id="file" data-file="${id}" data-folder="${id_folder}" data-type="${extension}">
                <div>    
                    <p style="margin-bottom: 0; word-break: break-all;">${name}</p>
                </div>
                <div class="d-flex justify-content-end">
                    <a href="#" id="${id}" class="favori-home" onclick="event.stopPropagation();">
                        <i class="fa-solid fa-star fa-lg me-2" style="color: #FFD43B;"></i>
                    </a>
                    <a href="#" id="${id}" class="desktop" onclick="event.stopPropagation();">
                        <i class="fa-regular fa-square-plus fa-lg" id="desk-home-${id}"></i>
                    </a>
                </div>
            </div>
        `;
    
        let favPanel = document.getElementById("aside-favorites");
        favPanel.appendChild(div);
        panelAfterRender();
        desktopAfterRender();
        previewAfterRender();
    }


    // Get the accordions list from the local storage
    let accordionList = JSON.parse(localStorage.getItem('accordion'));
    if (accordionList === null) {
        accordionList = [];
        localStorage.setItem('accordion', JSON.stringify(accordionList));
    }

    accordionList.forEach(
        accordion => {
            let accordionElement = document.getElementById(accordion);
            let accordionButton = document.getElementById(accordion + "-button");
            accordionElement.classList.add('show');
            accordionButton.setAttribute('aria-expanded', 'true');
        }
    );

    // Handle the accordions buttons
    let accordions = document.querySelectorAll('.accordion-collapse');
        accordions.forEach(
            accordion => {
                accordion.addEventListener('show.bs.collapse', function (event) {
                    event.stopPropagation();
                    let id = accordion.id;
                    let accordionList = JSON.parse(localStorage.getItem('accordion'));
                    accordionList.push(id);
                    localStorage.setItem('accordion', JSON.stringify(accordionList));
                });

                accordion.addEventListener('hide.bs.collapse', function (event) {
                    event.stopPropagation();
                    let id = accordion.id;
                    let accordionList = JSON.parse(localStorage.getItem('accordion'));
                    accordionList = accordionList.filter(accordion => accordion !== id);
                    localStorage.setItem('accordion', JSON.stringify(accordionList));
                });
            }
        )

    // prevent the accordion to close when clicking on the input
    const folders = document.querySelectorAll('.folder-item');
    folders.forEach((folder) => {
        folder.addEventListener('click', function (event) {
            event.stopPropagation();
            if (event.target.dataset.triggerAccordion === undefined) {
                var collapse = new bootstrap.Collapse(folder.parentElement.parentElement.querySelector('.accordion-collapse'));
                collapse.show();
            }
        });
    });

    const socket = io.connect('/home');

    // Handle dynamique search inside a folder
    let folderSearch = document.querySelectorAll("#fileSearch");
    folderSearch.forEach((folder) => {
        folder.addEventListener('input', function () {
            let folderId = folder.getAttribute("data-folder");
            let search = folder.value;
            socket.emit('search_files', { folderId: folderId, query: search });
        });
    });

    // Display the correct results for a specific folder research
    socket.on('search_results', function (data) {
        let fileContainer = document.getElementById("fichierAccordion"+data.folderId);
        let fileElements = fileContainer.querySelectorAll('.file-element');
        let countElement = document.getElementById('collapse'+data.folderId+'-button').querySelector('#fileCount');
        if (data.query === "") {
            fileElements.forEach(file => {
                file.style.display = "block";
                countElement.innerHTML = fileElements.length;
            });
        }
        else {
            fileElements.forEach(file => {
                let id = file.id.split("-")[1];
                if (data.results.includes(id)) {
                    file.style.display = "block";
                }
                else {
                    file.style.display = "none";
                }
                countElement.innerHTML = data.results.length;
            });
        }
    });

    // Handle de dynamique search for the links in the right panal
    let searchLink = document.getElementById("search-link");
    let links = document.querySelectorAll(".link-element");
    searchLink.addEventListener('input', function () {
        let search = searchLink.value;
        if (search === "") {
            links.forEach(link => {
                link.style.display = "block";
            });
        }
        else {
            links.forEach(link => {
                let name = link.querySelector(".link-name").innerHTML;
                let description = link.querySelector(".link-description").innerHTML;
                if (name.toLowerCase().includes(search.toLowerCase()) | description.toLowerCase().includes(search.toLowerCase())) {
                    link.style.display = "block";
                }
                else {
                    link.style.display = "none";
                }
            });
        }
    });

    function createErrorAlertMessage(message, data) {
        Swal.fire({
            position: 'top-end',
            icon: 'error',
            title: message,
            text: data.error,
            showConfirmButton: false,
            timer: 2000,
            backdrop: false
        });
    }
    
});