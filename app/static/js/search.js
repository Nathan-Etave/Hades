document.addEventListener('DOMContentLoaded', function() {
    let advancedSearchButton = document.getElementById("bouton_recherche_avance");
    let advancedSearchForm = document.querySelector(".advanced_search_popup");

    advancedSearchButton.addEventListener('click', function() {
        if (advancedSearchForm.style.display == "block") {
            advancedSearchForm.style.display = "none";
        } else {
            advancedSearchForm.style.display = "block";
        }
    }
    );
});