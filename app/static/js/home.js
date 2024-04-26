import { baseAfterRender } from './base.js';

document.addEventListener('DOMContentLoaded', function () {

    let btn_and = document.getElementById("btn_and");
    let btn_or = document.getElementById("btn_or");
    let search_bar = document.getElementById("search-bar");
    let csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    btn_and.addEventListener('click', function () {
        search_bar.value += " & ";
    });

    btn_or.addEventListener('click', function () {
        search_bar.value += " | "
    });

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
                .then(response => response.json())
                .then(data => {
                    if (data.status === "ok") {
                        let div_fav = document.querySelector(".fav"+id);
                        div_fav.remove();
                    }
                    else {
                        alert("Erreur lors de la suppression du favori");
                    }
                });
        });
    });

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

    let search_tiles = document.querySelectorAll(".search_term");
    let search_btn = document.getElementById("search_btn");
    search_tiles.forEach(function (tile) {
        tile.addEventListener('click', function () {
            search_bar.value = tile.getAttribute("query");
            search_btn.click();
        });
    });

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
});