document.addEventListener('DOMContentLoaded', function () {
    let progressBar = document.querySelector('.progress-bar');
    let fileInput = document.querySelectorAll('.file-input');
    let fileTotal = 0
    let fileUploadTotal = 0
    let csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    fileInput.forEach((input) => {
        input.addEventListener('change', async function (event) {
            let tags = prompt('Veuillez entrer les tags communs à tous les fichiers séparés par un point-virgule, ou laissez vide pour ne pas ajouter de tags.');
            if (tags === null) {
                event.target.value = '';
                return;
            }
            let folderId = event.target.dataset.folder;
            let files = event.target.files;
            fileTotal += files.length;
            for (let file of files) {
                await new Promise((resolve, reject) => {
                    let reader = new FileReader();
                    reader.onload = async function (ev) {
                        progressBar.style.width = `${(fileUploadTotal / fileTotal) * 100}%`;
                        progressBar.ariaValueNow = `${(fileUploadTotal / fileTotal) * 100}`;
                        progressBar.innerHTML = `${fileUploadTotal} / ${fileTotal}`;
                        let response = await fetch('/administration/upload', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrfToken
                            },
                            body: JSON.stringify({
                                folderId: folderId,
                                filename: file.name,
                                data: ev.target.result,
                                tags: tags
                            })
                        });
                        let status = await response.status;
                        if (status === 200) {
                            fileUploadTotal++;
                            progressBar.style.width = `${(fileUploadTotal / fileTotal) * 100}%`;
                            progressBar.ariaValueNow = `${(fileUploadTotal / fileTotal) * 100}`;
                            progressBar.innerHTML = `${fileUploadTotal} / ${fileTotal}`;
                            resolve();
                        }
                    }
                    reader.readAsDataURL(file);
                });
            }
            event.target.value = '';
        });
    });

    const socket = io.connect('/administration');

    socket.on('worker_status', function (data) {
        const workers = [
            document.querySelector('#workerStatusTable1 tbody'),
            document.querySelector('#workerStatusTable2 tbody')
        ];
        const nextFile = document.querySelector('#nextFile');

        for (let worker of workers) {
            if (worker.dataset.worker == data.worker) {
                worker.innerHTML = `
            <tr>
                <td>${data.status == 'processing' ? data.file : 'En attente'}</td>
            </tr>
            `;
            }
            else if (worker.dataset.worker == undefined) {
                worker.dataset.worker = data.worker;
                worker.innerHTML = `
            <tr>
                <td>${data.status == 'processing' ? data.file : 'En attente'}</td>
            </tr>
            `;
                break;
            }
        }

        nextFile.innerHTML = data.next_file == null ? 'Aucun fichier en attente' : JSON.parse(data.next_file).filename;
    });

    socket.on('total_files', function (data) {
        document.querySelector('#totalFiles').innerHTML = data;
    });

    socket.on('total_files_processed', function (data) {
        document.querySelector('#totalFilesProcessed').innerHTML = data;
    });

    const trashBtn = document.querySelectorAll('#trash-btn');
    trashBtn.forEach((btn) => {
        btn.addEventListener('click', async function (event) {
            let fileId = event.target.dataset.file;
            let folderId = event.target.dataset.folder
            socket.emit('trash_file', { fileId: fileId, folderId: folderId });
        });
    });

    socket.on('file_deleted', function (data) {
        let file = document.querySelector(`#file-${data.fileId}`);
        file.remove();
        let fileCount = document.querySelector(`.folder-${data.folderId}`).querySelector('#fileCount').innerHTML;
        fileCount--;
        document.querySelector(`.folder-${data.folderId}`).querySelector('#fileCount').innerHTML = fileCount;
    });

    socket.on('file_deletion_failed', function (data) {
        alert('La suppression du fichier a échoué.');
    });

    const folders = document.querySelectorAll('#folder');
    const searchBars = [];
    const intialFiles = {};
    folders.forEach((folder) => {
        searchBars.push(folder.querySelector('#fileSearch'));
        intialFiles[folder.dataset.folder] = folder.querySelector(`#filesAccordion${folder.dataset.folder}`).children;
    });

    let lastInputEvent = null;
    searchBars.forEach((searchBar) => {
        searchBar.addEventListener('input', function (event) {
            lastInputEvent = event;
            if (event.target.value === '') {
                Array.from(intialFiles[event.target.dataset.folder]).forEach((file) => {
                    file.style.display = 'block';
                });
                let fileCount = document.querySelector(`.folder-${event.target.dataset.folder}`).querySelector('#fileCount').innerHTML;
                fileCount = Array.from(intialFiles[event.target.dataset.folder]).length;
                document.querySelector(`.folder-${event.target.dataset.folder}`).querySelector('#fileCount').innerHTML = fileCount;
            }
            else {
                Array.from(intialFiles[event.target.dataset.folder]).forEach((file) => {
                    file.style.display = 'none';
                });
                socket.emit('search_files', { folderId: event.target.dataset.folder, query: event.target.value });
            }
        });
    });

    socket.on('search_results', function (data) {
        data.forEach((file) => {
            document.querySelector(`#file-${file.id}`).style.display = 'block';
        });
        if (data.length > 0) {
            let fileCount = document.querySelector(`.folder-${data[0].path}`).querySelector('#fileCount').innerHTML;
            fileCount = data.length;
            document.querySelector(`.folder-${data[0].path}`).querySelector('#fileCount').innerHTML = fileCount;
        }
        else {
            document.querySelector(`.folder-${lastInputEvent.target.dataset.folder}`).querySelector('#fileCount').innerHTML = 0;
        }
    });

    const roleSelects = document.querySelectorAll('.role-select');
    roleSelects.forEach((select) => {
        select.addEventListener('change', async function (event) {
            let userId = event.target.dataset.user;
            socket.emit('update_user_role', { userId: userId, roleId: event.target.value });
        });
    });

    socket.on('user_role_updated', function (data) {
        document.querySelector('.user-alert').appendChild(createAlert('success', data.message));
    });

    socket.on('user_role_not_updated', function (data) {
        document.querySelector('.user-alert').appendChild(createAlert('danger', data.error));
        document.querySelector(`#role-select-${data.userId}`).value = data.roleId;
    });

    const statusToggles = document.querySelectorAll('.status-toggle');
    statusToggles.forEach((toggle) => {
        toggle.addEventListener('change', async function (event) {
            let userId = event.target.dataset.user;
            socket.emit('update_user_status', { userId: userId, status: event.target.checked });
        });
    });

    socket.on('user_status_updated', function (data) {
        document.querySelector('.user-alert').appendChild(createAlert('success', data.message));
    });

    socket.on('user_status_not_updated', function (data) {
        document.querySelector('.user-alert').appendChild(createAlert('danger', data.error));
        let statusToggle = document.querySelector(`#status-toggle-${data.userId}`);
        statusToggle.parentElement.classList.remove('off');
        statusToggle.parentElement.classList.replace('btn-danger', 'btn-success');
    });

    const deleteUserButtons = document.querySelectorAll('.delete-user-button');
    deleteUserButtons.forEach((button) => {
        button.addEventListener('click', async function (event) {
            let userId = event.target.dataset.user;
            let confirmation = confirm('Voulez-vous vraiment supprimer cet utilisateur ?');
            if (!confirmation) return;
            socket.emit('delete_user', { userId: userId });
        });
    });

    socket.on('user_deleted', function (data) {
        document.querySelector('.user-alert').appendChild(createAlert('success', data.message));
        document.querySelector(`#user-${data.userId}`).remove();
    });

    socket.on('user_not_deleted', function (data) {
        document.querySelector('.user-alert').appendChild(createAlert('danger', data.error));
    });

    function createAlert(type, message) {
        let alert = document.createElement('div');
        alert.classList.add('alert', `alert-${type}`, 'alert-dismissible');
        alert.innerHTML = `<p class="mb-0">${message}</p><button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
        setTimeout(() => {
            alert.remove();
        }, 5000);
        return alert;
    }

    const searchUser = document.querySelector('#searchUser');
    const initialUsers = Array.from(document.querySelectorAll('.user'));
    searchUser.addEventListener('input', function (event) {
        if (event.target.value === '') {
            initialUsers.forEach((user) => {
                user.style.display = 'block';
            });
        }
        else {
            initialUsers.forEach((user) => {
                user.style.display = 'none';
            });
            let search = event.target.value.toLowerCase();
            initialUsers.forEach((user) => {
                let firstname = user.dataset.firstname.toLowerCase();
                let lastname = user.dataset.lastname.toLowerCase();
                let email = user.dataset.email.toLowerCase();
                if (firstname.includes(search) || lastname.includes(search) || email.includes(search)) {
                    user.style.display = 'block';
                }
            });
        }
    });

    folders.forEach((folder) => {
        folder.addEventListener('click', function (event) {
            event.stopPropagation();
            if (event.target.dataset.triggerAccordion !== undefined) {
                var collapse = new bootstrap.Collapse(folder.querySelector('.accordion-collapse'));
                collapse.show();
            }
        });
    });

    const modalParentFolders = document.querySelectorAll('#parentFolder');
    const modalExistingFolders = document.querySelector('#existingFolder');
    folders.forEach((folder) => {
        modalParentFolders.forEach((select) => {
            select.innerHTML += `<option value="${folder.dataset.folder}">${folder.dataset.name}</option>`;
        });
        modalExistingFolders.innerHTML += `<option value="${folder.dataset.folder}">${folder.dataset.name}</option>`;
    });

    const modifyFolderModal = document.querySelector('#modifyFolderModal');
    modalExistingFolders.addEventListener('change', function (event) {
        let folderId = event.target.value;
        if (folderId == '0') {
            modifyFolderModal.querySelector('#folderName').value = '';
            modifyFolderModal.querySelector('#parentFolder').value = '0';
            modifyFolderModal.querySelectorAll('.role-checkbox:checked').forEach((cb) => {
                cb.checked = false;
            });
            modifyFolderModal.querySelector('#folderColor').value = '#000000';
            return;
        }
        let folderArray = Array.from(folders);
        let folder = folderArray.find(f => f.dataset.folder == folderId);
        modifyFolderModal.querySelector('#folderName').value = folder.dataset.name;
        modifyFolderModal.querySelector('#parentFolder').value = folder.dataset.parent;
        folder.dataset.roles.split(',').forEach((role) => {
            if (role !== '1') {
                modifyFolderModal.querySelector(`#role${role}`).checked = true;
            }
        });
        modifyFolderModal.querySelector('#folderColor').value = folder.dataset.color;
    });

    const addFolderModal = document.querySelector('#addFolderModal');
    const createFolderButton = document.querySelector('#createFolderButton');
    createFolderButton.addEventListener('click', function (event) {
        if (fileTotal != fileUploadTotal) {
            return;
        }
        let folderName = addFolderModal.querySelector('#folderName').value;
        let parentFolderId = addFolderModal.querySelector('#parentFolder').value;
        let folderRoles = Array.from(addFolderModal.querySelectorAll('.role-checkbox:checked')).map(cb => cb.value);
        let folderColor = addFolderModal.querySelector('#folderColor').value;
        createFolderButton.disabled = true;
        if (folderName !== '') {
            socket.emit('create_folder', { folderName: folderName, parentFolderId: parentFolderId, folderRoles: folderRoles, folderColor: folderColor });
        }
        else {
            alert('Veuillez remplir tous les champs.');
            createFolderButton.disabled = false;
        }
    });

    socket.on('folder_created', function (data) {
        window.location.reload();
    });

    socket.on('folder_not_created', function (data) {
        alert(`La création du dossier a échoué: ${data.error}`);
        createFolderButton.disabled = false;
    });

    const formCreateFolder = document.querySelector('#addFolderModal').querySelector('form');
    formCreateFolder.addEventListener('submit', function (event) {
        if (fileTotal != fileUploadTotal) {
            event.preventDefault();
            alert('Veuillez attendre la fin du téléversement des fichiers avant de créer un dossier.');
            return;
        }
    });

    const modifyFolderButton = document.querySelector('#modifyFolderButton');
    modifyFolderButton.addEventListener('click', function (event) {
        if (fileTotal != fileUploadTotal) {
            return;
        }
        let folderId = modifyFolderModal.querySelector('#existingFolder').value;
        let folderName = modifyFolderModal.querySelector('#folderName').value;
        let parentFolderId = modifyFolderModal.querySelector('#parentFolder').value;
        let folderRoles = Array.from(modifyFolderModal.querySelectorAll('.role-checkbox:checked')).map(cb => cb.value);
        let folderColor = modifyFolderModal.querySelector('#folderColor').value;
        modifyFolderButton.disabled = true;
        if (folderName !== '' && folderId !== '0') {
            socket.emit('modify_folder', { folderId: folderId, folderName: folderName, parentFolderId: parentFolderId, folderRoles: folderRoles, folderColor: folderColor });
        }
        else {
            alert('Veuillez remplir tous les champs.');
            modifyFolderButton.disabled = false;
        }
    });

    socket.on('folder_modified', function (data) {
        window.location.reload();
    });

    socket.on('folder_not_modified', function (data) {
        alert(`La modification du dossier a échoué: ${data.error}`);
        modifyFolderButton.disabled = false;
    });

    const formModifyFolder = document.querySelector('#modifyFolderModal').querySelector('form');
    formModifyFolder.addEventListener('submit', function (event) {
        if (fileTotal != fileUploadTotal) {
            event.preventDefault();
            alert('Veuillez attendre la fin du téléversement des fichiers avant de modifier un dossier.');
            return;
        }
    });
}); 