document.addEventListener('DOMContentLoaded', function() {
    let addCategoryForm = document.querySelector('.add_category_form');
    let updateCategoryForm = document.querySelector('.update_category_form');
    let deleteCategoryButton = document.getElementById('delete_category_button');
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
    addCategoryForm.addEventListener('submit', function() {
        let lastCategories = getLastCategories();
        if (addCategoryForm.querySelector('input').value === '') {
            alert('Veuillez entrer un nom de catégorie.');
            return;
        }
        if (lastCategories.length === 0) {
            fetch('/add_category', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'categoryName': addCategoryForm.querySelector('input').value,
                    'parentId': null
                })
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                }
            });
        }
        else if (lastCategories.length > 1) {
            alert('Veuillez sélectionner une seule catégorie.');
            return;
        }
        else {
            if (lastCategories[0] == '1') {
                alert('Vous ne pouvez pas ajouter de catégorie à cette catégorie.');
                return;
            }
            else {
                fetch('/add_category', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        'categoryName': addCategoryForm.querySelector('input').value,
                        'parentId': lastCategories[0]
                    })
                })
                .then(response => {
                    if (response.redirected) {
                        window.location.href = response.url;
                    }
                });
            }
        }
    });
    updateCategoryForm.addEventListener('submit', function() {
        let lastCategories = getLastCategories();
        if (lastCategories.length === 0) {
            alert('Veuillez sélectionner une catégorie.');
            return;
        }
        else if (lastCategories.length > 1) {
            alert('Veuillez sélectionner une seule catégorie.');
            return;
        }
        else {
            if (updateCategoryForm.querySelector('input').value === '') {
                if (lastCategories[0] == '1') {
                    alert('Vous ne pouvez pas modifier cette catégorie.');
                    return;
                }
                else {
                    updateCategoryForm.querySelector('input').value = document.querySelector('input[id="' + lastCategories[0] + '"]').parentElement.querySelector('label').innerText;
                    updateCategoryForm.querySelector('input').readOnly = false;
                    updateCategoryForm.querySelector('input').hidden = false;
                    updateCategoryForm.querySelector('button').innerText = 'Valider la modification';
                }
            }
            else {
                if (lastCategories[0] == '1') {
                    alert('Vous ne pouvez pas modifier cette catégorie.');
                    return;
                }
                else if (updateCategoryForm.querySelector('input').value === document.querySelector('input[id="' + lastCategories[0] + '"]').parentElement.querySelector('label').innerText) {
                    alert('Veuillez entrer un nom de catégorie différent de l\'ancien.');
                    return;
                }
                else {
                    fetch('/update_category', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            'categoryName': updateCategoryForm.querySelector('input').value,
                            'categoryId': lastCategories[0]
                        })
                    })
                    .then(response => {
                        if (response.redirected) {
                            window.location.href = response.url;
                        }
                    });
                }
            }
        }
    });
    deleteCategoryButton.addEventListener('click', function() {
        let lastCategories = getLastCategories();
        if (lastCategories.length === 0) {
            alert('Veuillez sélectionner une catégorie.');
            return;
        }
        else if (lastCategories.length > 1) {
            alert('Veuillez sélectionner une seule catégorie.');
            return;
        }
        else {
            if (lastCategories[0] == '1') {
                alert('Vous ne pouvez pas supprimer cette catégorie.');
                return;
            }
            else {
                fetch('/delete_category', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        'categoryId': lastCategories[0]
                    })
                })
                .then(response => {
                    if (response.redirected) {
                        window.location.href = response.url;
                    }
                });
            }
        }
    });
    function getLastCategories() {
        let lastCategories = [];
        for (let tree of document.querySelectorAll('.category_list_container ul li')) {
            let selectedCategories = Array.from(tree.querySelectorAll('input:checked'));
            if (selectedCategories.length > 0) {
                let lastCategory = selectedCategories[selectedCategories.length - 1];
                if (!lastCategories.includes(lastCategory.id)) {
                    lastCategories.push(lastCategory.id);
                }
            }
        }
        return lastCategories;
    }
});