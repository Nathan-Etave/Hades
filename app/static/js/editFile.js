document.addEventListener('DOMContentLoaded', function() {
    let generateTagsButton = document.querySelectorAll('.automatic_tags_generation')[0];
    let tagForm = generateTagsButton.parentElement.querySelector('form');
    let tagsList = document.querySelector('.tags_list');
    let updateButton = document.querySelector('#update_button');
    let deleteButton = document.querySelector('#delete_button');
    let categoriesList = document.getElementsByClassName('category');
    let validateButton = document.querySelector('#validate_button');
    let oldFileId = document.querySelector('.file_id').textContent;
    let file = null;
    let reader = new FileReader();
    categoriesList = Array.from(categoriesList).map(function(category) {
        return category.textContent;
    });
    let willBeUpdated = false;
    let willBeDeleted = false;
    if (Array.from(tagsList.querySelectorAll('li')).length > 0 || isImageFile(generateTagsButton.name)) {
        generateTagsButton.disabled = true;
    }
    for (let tag of tagsList.querySelectorAll('li')) {  
        tag.addEventListener('click', function() {
            tag.remove();
            if (tagsList.querySelectorAll('li').length === 0 && !isImageFile(generateTagsButton.name)) {
                generateTagsButton.disabled = false;
            }
        });
    }
    function isImageFile(fileName) {
        const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.JPG', '.JPEG', '.PNG', '.GIF'];
        return imageExtensions.some(extension => fileName.endsWith(extension));
    }
    generateTagsButton.addEventListener('click', function() {
        tagForm.querySelector('input').disabled = true;
        tagForm.querySelector('button').disabled = true;
        generateTagsButton.disabled = true;
        generateTagsButton.textContent = 'Generation des tags en cours...';
        fetch('generate_tags', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                filename: generateTagsButton.name
            })
        })
        .then(response => response.json())
        .then(result => {
            console.log(result);
            tagForm.querySelector('input').disabled = false;
            tagForm.querySelector('button').disabled = false;
            generateTagsButton.textContent = 'Générer automatiquement les tags';
            let ulList = generateTagsButton.parentElement.querySelector('div ul');
            for (let tag of result) {
                ulList.innerHTML += '<li>' + tag + '</li>';
            }
            for (let tag of ulList.querySelectorAll('li')) {
                tag.addEventListener('click', function() {
                    tag.remove();
                    if (ulList.querySelectorAll('li').length === 0 && !isImageFile(generateTagsButton.name)) {
                        generateTagsButton.disabled = false;
                    }
                });
            }
        });
    });
    tagForm.addEventListener('submit', function(event) {
        event.preventDefault();
        var ulElement = tagForm.parentElement.querySelector('div ul');
        ulElement.innerHTML += '<li title = "Cliquez pour supprimer">' + tagForm.querySelector('input').value + '</li>';
        tagForm.querySelector('input').value = '';
    });
    var ulElement = tagForm.parentElement.querySelector('div ul');
    ulElement.addEventListener('click', function(event) {
        if (event.target.tagName === 'LI') {
            event.target.remove();
            if (ulElement.querySelectorAll('li').length === 0 && !isImageFile(generateTagsButton.name)) {
                generateTagsButton.disabled = false;
            }
        }
    });
    updateButton.addEventListener('click', function() {
        let input = document.createElement('input');
        input.type = 'file';
        input.accept = '.pdf, .docx, .xlsx, .pptx, .txt, .jpg, .jpeg, .png, .gif';
        input.multiple = false;
        input.addEventListener('change', function() {
            file = input.files[0];
            reader = new FileReader();
            reader.onload = function(element) {
                let documentPreviewContainer = document.querySelector('.file_header');
                let mime_type = file.type;
                let src = element.target.result;
                fetch ('add_file_to_temp', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        filename: file.name,
                        fileData: src
                    })
                }).then(response => response.json())
                .then(result => {
                    let title = result;
                    if (mime_type.startsWith('image')) {
                        documentPreviewContainer.innerHTML = `<h2>${title}</h2><img class="file_object" src="${src}" alt="Impossible d'afficher le fichier">`;
                    } else {
                        documentPreviewContainer.innerHTML = `<h2>${title}</h2><object class="file_object" data="${src}" type="${mime_type}"><p>Impossible d'afficher le fichier</p></object>`;
                    }
                    generateTagsButton.name = title;
                    willBeUpdated = true;
                    if (!isImageFile(generateTagsButton.name) && Array.from(tagsList.querySelectorAll('li')).length === 0) {
                        generateTagsButton.disabled = false;
                    }
                });
            };
            if (file) {
                reader.readAsDataURL(file);
            }
        });
        input.click();
    });
    deleteButton.addEventListener('click', function() {
        if (confirm('Êtes-vous sûr de vouloir supprimer ce fichier ?')) {
            let documentPreviewContainer = document.querySelector('.file_container');
            documentPreviewContainer.style.justifyContent = 'center';
            documentPreviewContainer.innerHTML = '<h2 style="text-align: center;align-self: center; color: red;">Le fichier va être supprimé lors de la validation des modifications.<br>Annuler les modifications pour empêcher la suppression.</h2>';
            willBeDeleted = true;
        }
    });
    document.querySelectorAll('.category_checkbox').forEach(function(categoryCheckbox) {
        categoryCheckbox.addEventListener('click', function(event) {
            event.stopPropagation();
        });
        categoryCheckbox.addEventListener('change', function() {
            var detailsElement = this.closest('details');
            if (detailsElement) {
                detailsElement.open = this.checked;
            }
            var checkbox_id = this.id;
            if (this.checked) {
                var parent_id = this.dataset.parent;
                while (parent_id) {
                    var parentCheckbox = document.getElementById(parent_id);
                    if (parentCheckbox) {
                        parentCheckbox.checked = true;
                        parent_id = parentCheckbox.dataset.parent;
                    } else {
                        parent_id = null;
                    }
                }
            } else {
                var uncheckChildren = function(id) {
                    document.querySelectorAll('[data-parent=\'' + id + '\']').forEach(function(childCheckbox) {
                        childCheckbox.checked = false;
                        uncheckChildren(childCheckbox.id);
                    });
                };
                uncheckChildren(checkbox_id);
            }
        });
        if (categoriesList.includes(categoryCheckbox.id) && !categoryCheckbox.checked) {
            categoryCheckbox.checked = true;
            categoryCheckbox.dispatchEvent(new Event('change'));
        }
    });
    validateButton.addEventListener('click', function() {
        let json = {};
        let filename = null;
        for (let file of document.querySelectorAll('.file_container')) {
            if (willBeUpdated) {
                filename = file.querySelector('.file_header h2').textContent;
            }
            json[filename] = {};
            json[filename]['tags'] = [];
            json[filename]['categories'] = [];
            for (let tag of file.querySelectorAll('.tags_list li')) {
                json[filename]['tags'].push(tag.textContent);
            }
            for (let tree of file.querySelectorAll('.category_list_container ul li')) {
                let selectedCategories = Array.from(tree.querySelectorAll('input:checked'));
                if (selectedCategories.length > 0) {
                    let lastCategory = selectedCategories[selectedCategories.length - 1];
                    if (!json[filename]['categories'].includes(lastCategory.id)) {
                        json[filename]['categories'].push(lastCategory.id);
                    }
                }
            }
        }
        json[filename]['willBeUpdated'] = willBeUpdated;
        json[filename]['willBeDeleted'] = willBeDeleted;
        json[filename]['oldFileId'] = oldFileId;
        json[filename]['fileData'] = willBeUpdated ? reader.result : null;
        fetch ('update_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(json)
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            }
        });
        fetch('delete_all_temp_files', {
            method: 'POST'
        });
    });
});