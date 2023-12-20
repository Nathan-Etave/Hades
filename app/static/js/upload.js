document.addEventListener('DOMContentLoaded', function() {
    let autoUploadButton = document.getElementById("auto_upload_button");
    autoUploadButton.addEventListener('click', function() {
        let tags = prompt("Entrez les tags globaux à ajouter aux fichiers que vous téléversez automatiquement séparés par des points-virgules (ex: tag1;tag2;tag3):", "");
        document.querySelector("main").innerHTML = '<h2>Le téléversement automatique est en cours...</h2><h3>Cette page se rechargera automatiquement lorsque le téléversement sera terminé.</h3><h3>Le téléversement peut prendre plusieurs minutes si vous avez beaucoup de fichiers à téléverser.</h3>';
        fetch('/automatic_files_management', {
            method: 'POST',
            body: JSON.stringify({tags: tags}),
            headers: {'Content-Type': 'application/json'}
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            }
        });
    });
});