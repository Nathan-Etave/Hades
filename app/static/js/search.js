document.addEventListener('DOMContentLoaded', function() {
    let advancedSearchButton = document.getElementById("bouton_recherche_avance");
    let advancedSearchForm = document.querySelector(".advanced_search_popup");
    let downloadButtons = document.querySelectorAll(".bouton_telechargement");
    advancedSearchButton.addEventListener('click', function() {
        if (advancedSearchForm.style.display == "block") {
            advancedSearchForm.style.display = "none";
        } else {
            advancedSearchForm.style.display = "block";
        }
    });
    downloadButtons.forEach(function(downloadButton) {
        let fileId = downloadButton.id;
        downloadButton.addEventListener('click', function() {
            console.log(fileId);
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