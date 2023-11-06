document.addEventListener('DOMContentLoaded', function() {
    let addToMultiViewButton = document.getElementById('add_to_multiview');
    let downloadButton = document.getElementById('download');
    let addToFavouritesButton = document.getElementById('add_to_favourites');
    let reportButton = document.getElementById('report');
    let fileId = document.querySelector('h2').textContent.match(/\((\d+)\)/)[1]
    let reportPopup = document.querySelector('.report_popup');
    let reportPopupCloseButton = document.getElementById('cancel_report');
    let reportPopupSubmitButton = document.getElementById('send_report');
    let reportPopupReason = document.getElementById('message');

    downloadButton.addEventListener('click', function() {
        fetch('download_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({file_id: fileId})
        });
    }
    );

    addToMultiViewButton.addEventListener('click', function() {
        fetch('add_to_multiview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({file_id: fileId})
        });
    }
    );

    addToFavouritesButton.addEventListener('click', function() {
        fetch('add_to_favourites', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({file_id: fileId})
        });
    }
    );

    reportButton.addEventListener('click', function() {
        reportPopup.style.display = 'block';
    }
    );

    reportPopupCloseButton.addEventListener('click', function() {
        reportPopup.style.display = 'none';
    }
    );
    
    reportPopupSubmitButton.addEventListener('click', function() {
        let reportReason = reportPopupReason.value;
        if (reportReason.length > 0) {
            fetch('report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({file_id: fileId, reason: reportReason})
            }
            );
            reportPopup.style.display = 'none';
            alert('Le fichier a été signalé avec succès.');
        }
        else {
            alert('Veuillez entrer une raison pour le signalement.');
        }
    }
    );
  });