document.addEventListener('DOMContentLoaded', function() {
    let generateTagsButtons = document.querySelectorAll('.automatic_tags_generation');
    let addTagForms = document.querySelectorAll('.add_tag_form');
    let validateButton = document.querySelector('#validate_button');
    function isImageFile(fileName) {
        const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.JPG', '.JPEG', '.PNG', '.GIF'];
        return imageExtensions.some(extension => fileName.endsWith(extension));
    }
    generateTagsButtons.forEach(function(generateTagsButton) {
        if (isImageFile(generateTagsButton.name)) {
            generateTagsButton.disabled = true;
        }
        else {
            generateTagsButton.addEventListener('click', function() {
                generateTagsButton.parentElement.querySelector('form input').disabled = true;
                generateTagsButton.parentElement.querySelector('form button').disabled = true;
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
                    generateTagsButton.parentElement.querySelector('form input').disabled = false;
                    generateTagsButton.parentElement.querySelector('form button').disabled = false;
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
        }
    });
    addTagForms.forEach(function(addTagForm) {
        addTagForm.addEventListener('submit', function(event) {
            event.preventDefault();
            var ulElement = addTagForm.parentElement.querySelector('div ul');
            ulElement.innerHTML += '<li title = "Cliquez pour supprimer">' + addTagForm.querySelector('input').value + '</li>';
            addTagForm.querySelector('input').value = '';
        });

        var ulElement = addTagForm.parentElement.querySelector('div ul');
        ulElement.addEventListener('click', function(event) {
            if (event.target.tagName === 'LI') {
                event.target.remove();
                if (ulElement.querySelectorAll('li').length === 0 && !isImageFile(ulElement.parentElement.parentElement.querySelector('.automatic_tags_generation').name)) {
                    ulElement.parentElement.parentElement.querySelector('.automatic_tags_generation').disabled = false;
                }
            }
        });
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
    });
    validateButton.addEventListener('click', function() {
        let json = {};
        for (let file of document.querySelectorAll('.file_container')) {
            let filename = file.querySelector('.file_header h2').textContent;
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
        fetch('upload_files_to_database', {
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
    });
});