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

    let favorites_btn = document.querySelectorAll(".favori");
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
                        let div_fav = document.getElementById("fav" + id);
                        div_fav.remove();
                    }
                    else {
                        alert("Erreur lors de la suppression du favori");
                    }
                });
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
});