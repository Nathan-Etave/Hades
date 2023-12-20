document.addEventListener('DOMContentLoaded', function() {
    let advancedSearchButton = document.getElementById("bouton_recherche_avance");
    let advancedSearchForm = document.querySelector(".advanced_search_popup");
    let close = document.querySelector("#close");
    let validerRechercheAvanceButton = document.getElementById("valider_recherche_avance");
    let downloadButtons = document.querySelectorAll(".bouton_telechargement");

    // Charger les sélections précédentes depuis le stockage local
    function loadSelections() {
        let selectedCategories = JSON.parse(localStorage.getItem('selectedCategories')) || [];
        
        selectedCategories.forEach(function(categoryId) {
            let categoryCheckbox = document.getElementById(categoryId);
            if (categoryCheckbox) {
                categoryCheckbox.checked = true;
            }
        });

        let favoris = JSON.parse(localStorage.getItem('favoris')) || false;
        let date = JSON.parse(localStorage.getItem('date')) || false;
        let extension = JSON.parse(localStorage.getItem('extension')) || 'all';

        document.getElementById("favoris").checked = favoris;
        document.getElementById("date").checked = date;
        document.getElementById("extension").value = extension;
    }
    advancedSearchButton.addEventListener('click', function() {
        if (advancedSearchForm.style.display === "block") {
            advancedSearchForm.style.display = "none";
        } else {
            advancedSearchForm.style.display = "block";
        }

        // Charger les sélections lors de l'ouverture du formulaire
        loadSelections();
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

        if (favoris) {
            url += 'favoris=true&';
        }

        if (date) {
            url += 'recent=true&';
        }

        if (extension !== 'all') {
            url += 'extension=' + extension + '&';
        }

        let categories = document.querySelectorAll('.category_checkbox:checked');
        categories.forEach(function(category) {
            url += 'categorie=' + category.value + '&';
        });

        url = url.slice(0, -1);

        // Enregistrer les sélections dans le stockage local
        let selectedCategories = Array.from(categories).map(function(category) {
            return category.value;
        });
        localStorage.setItem('selectedCategories', JSON.stringify(selectedCategories));
        localStorage.setItem('favoris', JSON.stringify(favoris));
        localStorage.setItem('date', JSON.stringify(date));
        localStorage.setItem('extension', JSON.stringify(extension));

        // Recharger la page avec la nouvelle URL
        window.location.href = url;
    });

    // Charger les sélections lors du chargement initial de la page
    loadSelections();

    // Désélectionner les autres catégories lorsqu'une catégorie est sélectionnée
    let checkboxes = document.querySelectorAll('input[type="checkbox"].category_checkbox');
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            checkboxes.forEach(function(c) {
                if (c !== checkbox) c.checked = false;
            });
        });
    });
    downloadButtons.forEach(function(downloadButton) {
        let fileId = downloadButton.id;
        console.log(fileId);
        downloadButton.addEventListener('click', function() {
            fetch('download_file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    file_id: fileId
                })
            })
            .then(response => response.blob())
            .then(blob => {
                let downloadLink = document.createElement('a');
                blob.text().then(function(result) {
                    let file_data = result;
                    downloadLink.href = 'data:application/octet-stream;base64,' + file_data;
                    downloadLink.download = downloadButton.parentElement.querySelector('#bouton_fichier').textContent;
                    downloadLink.click();
                    downloadLink.remove();
                });
            });
        });
    });
});

