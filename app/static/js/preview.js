function previewButton(document){
    let previewFiles = document.querySelectorAll('.fichier');
    previewFiles.forEach(function(button) {
        let id = button.id;
        button.addEventListener('click', function(event) {
            event.preventDefault();
            fetch('/previsualisation/' + id, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.blob())
            .then(blob => {
                blob.text().then(function(result) {
                    let previewBox = document.getElementById('preview_box');
                    if(previewBox.getElementsByClassName('file_object').length > 0){
                        previewBox.removeChild(previewBox.getElementsByClassName('file_object')[0]);
                    }
                    let type = document.getElementById('type_'+id).innerHTML;
                    let mime_type;
                    let preview;
                    switch(type){
                        case 'jpg':
                            mime_type = 'image/jpg';
                            break;
                        case 'jpeg':
                            mime_type = 'image/jpeg'; 
                            break;
                        case 'gif':
                            mime_type = 'image/gif';
                            break;
                        case 'png':
                            mime_type = 'image/png';
                            break;
                        case 'pdf':
                            mime_type = 'application/pdf';
                            break;
                        case 'txt':
                            mime_type = 'text/plain';
                            break;
                    }
                    if(mime_type.startsWith('image')){
                        preview = document.createElement('img');
                        preview.src = 'data:'+mime_type+';base64,'+result;
                        preview.className = 'file_object';
                        preview.alt = 'Impossible d\'afficher le fichier';
                        previewBox.appendChild(preview);
                    }
                    else{
                        preview = document.createElement('object');
                        preview.data = 'data:'+mime_type+';base64,'+result;
                        preview.type = mime_type;
                        preview.className = 'file_object';
                        previewBox.appendChild(preview);
                    }
                });
            });
        });
    });
}
