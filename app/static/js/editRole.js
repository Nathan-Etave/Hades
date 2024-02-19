document.addEventListener('DOMContentLoaded', function() {
    var url_string = window.location.href;
    var url = new URL(url_string);
    var role = url.searchParams.get("role");
    if (role) {
        var selectElement = document.getElementById("SelectRole");
        var selectedOptions = Array.from(selectElement.options)
                                    .filter(option => option.value == role)
                                    .map(option => option.value);
        selectElement.value = selectedOptions[0];
    }
    document.getElementById("SelectRole").addEventListener("change", function() {
        var selectElement = document.getElementById("SelectRole");
        var selectedOptions = Array.from(selectElement.options)
                                    .filter(option => option.selected)
                                    .map(option => option.value);
        var idRoles = selectedOptions.join(",");
        var url = window.location.href.split('?')[0] + "?role=" + idRoles;
        window.location.href = url;
    });
    Array.from(document.querySelectorAll('#delete_user_role')).forEach(function(element) {
        element.addEventListener('click', function() {
            let idPompier = element.parentElement.querySelector('a').href.split('=')[1];
            fetch ('/edit_user_role', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    idPompier: idPompier,
                    idRole: 2
                })
            }).then( response => {
                if (response.redirected) {
                    window.location.href = response.url;
                }
            });
        });
    });

    document.querySelector('#valider').addEventListener('click', function(event) {
        event.preventDefault(); // Prevent the form from being submitted
        let inputValue = document.querySelector('input[name="search"]').value;
        console.log(inputValue); // Output the value to the console

        var selectElement = document.getElementById("SelectRole");
        var selectedOptions = Array.from(selectElement.options)
                                    .filter(option => option.selected)
                                    .map(option => option.value);
        var idRoles = selectedOptions.join(",");

        fetch('/add_user_role', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mail: inputValue,
                idRole: idRoles
            })
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            }
        })
        .catch(error => console.error('Error:', error));
    });
    document.getElementById("modify_role").addEventListener("change", function() {
        var selectElement = document.getElementById("modify_role");
        var selectedOptions = Array.from(selectElement.options)
                                    .filter(option => option.selected)
                                    .map(option => option.value);
        var idRoles = selectedOptions.join(",");
        fetch ('/get_role_categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                idRole: idRoles
            })
        }).then (response => response.json())
        .then (data => {
            let categories = document.querySelectorAll('.category_list_container_modifier ul li input');
            for (let category of categories) {
                category.checked = false;
            }
            for (let category of data) {
                let categoryElement = document.getElementById(category);
                categoryElement.checked = true;
            }
        });
    });
    document.querySelector('#modification_button').addEventListener('click', function(event) {
        let categoryLeaves = getAllSelectedCategoriesModify();
        var selectedOptions = Array.from(document.getElementById("modify_role").options)
                                    .filter(option => option.selected)
                                    .map(option => option.value);
        var idRoles = selectedOptions.join(",");
        fetch ('/modify_role_categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                idRole: idRoles,
                categories: categoryLeaves
            })
        }).then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            }
        });
    });

    document.querySelector('#creation_button').addEventListener('click', function(event) {
        let nomRoleValue = document.querySelector('#nomRole').value;
        let descriptionRoleValue = document.querySelector('#descriptionRole').value;
        fetch ('/add_role', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nomRole: nomRoleValue,
                description: descriptionRoleValue,
                categories: getAllSelectedCategories()
            })
        }).then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            }
        });
    });

    function getAllSelectedCategoriesModify() {
        let selectedCategories = [];
        for (let tree of document.querySelectorAll('.category_list_container_modifier ul li')) {
            let selectedCategoriesTree = Array.from(tree.querySelectorAll('input:checked'));
            for (let category of selectedCategoriesTree) {
                if (!selectedCategories.includes(category.value)) {
                    selectedCategories.push(category.value);
                }
            }
        }
        return selectedCategories;
    }
    function getAllSelectedCategories() {
        let selectedCategories = [];
        for (let tree of document.querySelectorAll('.category_list_container_ajouter ul li')) {
            let selectedCategoriesTree = Array.from(tree.querySelectorAll('input:checked'));
            for (let category of selectedCategoriesTree) {
                if (!selectedCategories.includes(category.value)) {
                    selectedCategories.push(category.value);
                }
            }
        }
        return selectedCategories;
    }
});