import { baseAfterRender } from './base.js';

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
                        }
                        else {
                            alert("Erreur lors de la suppression du favori");
                        }
                    });
            });
        });
    }

    //apply the JS the first time
    panelAfterRender();

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
                                console.log(favTile);
                                console.log(id);
                                if (favTile !== null) {
                                    favTile.remove();
                                }
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
                        .then(response => response.json().then(data => ({ status: response.status, body: data })))
                        .then(data => {
                            if (data.status === 200) {
                                fav.className = "favori-true";
                                etoile.className = "fa-solid fa-star fa-lg me-2";
                                let elem = fav.parentElement.parentElement.querySelector("#file");
                                displayFav(elem.getAttribute("data-file"), elem.getAttribute("data-name"), elem.getAttribute("data-folder"), elem.getAttribute("data-type"));
                                panelAfterRender();
                            }
                            else {
                                alert("Erreur lors de l'ajout du favori");
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
                <p style="margin-bottom: 0; word-break: break-all;">${name}</p>
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
    }

    // Handle previous seartch terms in the side panel
    let search_tiles = document.querySelectorAll(".search_term");
    let search_btn = document.getElementById("search_btn");
    search_tiles.forEach(function (tile) {
        tile.addEventListener('click', function () {
            search_bar.value = tile.getAttribute("query");
            search_btn.click();
        });
    });

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
                deskHomeBtn.className = "fa-regular fa-square-minus fa-lg";
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
                    deskHomeBtn.className = "fa-regular fa-square-plus fa-lg";
                }
                else {
                    newDeskList.push(fileId);
                    localStorage.setItem('desktop', JSON.stringify(newDeskList));
                    desktop.className = "desktop-true";
                    deskBtn.className = "fa-regular fa-square-minus fa-lg";
                    deskHomeBtn.className = "fa-regular fa-square-minus fa-lg";
                }
                baseAfterRender(newDeskList.length);
            });
        }
    );
});