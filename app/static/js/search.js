document.addEventListener('DOMContentLoaded', function() {
    let advancedSearchButton = document.getElementById("bouton_recherche_avance");
    let advancedSearchForm = document.querySelector(".advanced_search_popup");
    let close = document.querySelector("#close");
    let validerRechercheAvanceButton = document.getElementById("valider_recherche_avance");

    advancedSearchButton.addEventListener('click', function() {
        if (advancedSearchForm.style.display === "block") {
            advancedSearchForm.style.display = "none";
        } else {
            advancedSearchForm.style.display = "block";
        }
    });

    close.addEventListener('click', function() {
        console.log("Close button clicked");
        advancedSearchForm.style.display = "none";
    });

    

                validerRechercheAvanceButton.addEventListener('click', function() {
                    let extension = document.getElementById("extension").value;
                    let favoris = document.getElementById("favoris").checked;
                    let date = document.getElementById("date").checked;

                    // Construire l'URL avec les paramètres de filtrage
                    let url = window.location.href.split('?')[0] + '?';

                    if (extension !== 'all') {
                        url += 'extension=' + extension + '&';
                    }

                    if (favoris) {
                        url += 'favoris=true&';
                    }

                    if (date) {
                        url += 'recent=true&';
                    }

                    
                    url = url.slice(0, -1);

                    // Recharger la page avec la nouvelle URL
                    window.location.href = url;
                    //garder les paramètres de recherche dans le formulaire
                });
});