document.addEventListener('DOMContentLoaded', function() {
    let downloadButtons = document.querySelectorAll(".bouton_telechargement");
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