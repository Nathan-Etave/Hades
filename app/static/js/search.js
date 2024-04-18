document.addEventListener('DOMContentLoaded', function() {
    let favs = document.querySelectorAll('.favori');
    let csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    favs.forEach(function(fav) {
        let id = fav.id;
        let isFav = fav.getAttribute('is-fav');
        let etoile = document.getElementById("fav-"+id);
        if (isFav === "True") {
            fav.className = "favori-true";
        }
        else {
            fav.className = "favori-false";
            etoile.className = "fa-regular fa-star fa-lg";
        }
        fav.addEventListener('click', function(event) {
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
                    if (data.status === "ok"){
                        fav.className = "favori-false";
                        etoile.className = "fa-regular fa-star fa-lg";
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
                    if (data.status === "ok"){
                        fav.className = "favori-true";
                        etoile.className = "fa-solid fa-star fa-lg";
                    }
                    else {
                        alert("Erreur lors de l'ajout du favori");
                    }
                });
            }
        });
    });
});