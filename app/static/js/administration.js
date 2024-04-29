document.addEventListener('DOMContentLoaded', function () {

    let checkboxes = document.querySelectorAll('input[type=checkbox]');
    checkboxes.forEach((checkbox) => {
        checkbox.checked = false;
    });

    let dialogQueue = [];
    let dialogIsOpen = false;
    let progressBar = document.querySelector('.progress-bar');
    let fileInput = document.querySelectorAll('.file-input');
    let fileTotal = 0
    let fileUploadTotal = 0
    let csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    async function uploadFile(file, folderId, tags) {
        let reader = new FileReader();
        reader.onload = async function (ev) {
            updateProgressBar();
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
            let status = response.status;
            if (status === 200) {
                fileUploadTotal++;
                updateProgressBar();
            }
            else if (status === 409) {
                let data = await response.json();
                dialogQueue.push({
                    type: 'upload',
                    dialogOptions: {
                        title: 'Fichier existant',
                        text: `Un fichier nommé "${data.filename}" existe déjà dans le classeur ${data.existingFolder}. Ce fichier a été créé par ${data.existingFileAuthorFirstName} ${data.existingFileAuthorLastName} le ${data.existingFileDate}. Voulez-vous remplacer ce fichier et le placer dans le classeur ${data.attemptedFolder} ?`,
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonText: 'Oui',
                        cancelButtonText: 'Non',
                        allowOutsideClick: false,
                        allowEscapeKey: false
                    },
                    fileData: {
                        folderId: folderId,
                        filename: file.name,
                        data: ev.target.result,
                        tags: tags,
                        force: true
                    }
                });
                showNextDialog();
            }
        };
        reader.readAsDataURL(file);
    }

    fileInput.forEach((input) => {
        input.addEventListener('change', async function (event) {
            let { value: tags } = await Swal.fire({
                title: 'Tags communs',
                text: 'Veuillez entrer les tags communs à tous les fichiers séparés par un point-virgule, ou laissez vide pour ne pas ajouter de tags.',
                input: 'text',
                showCancelButton: true,
            });
            if (tags === undefined) {
                event.target.value = '';
                return;
            }
            let folderId = event.target.dataset.folder;
            let files = event.target.files;
            fileTotal += files.length;
            for (let file of files) {
                uploadFile(file, folderId, tags);
            }
            event.target.value = '';
        });
    });

    function updateProgressBar() {
        progressBar.style.width = `${(fileUploadTotal / fileTotal) * 100}%`;
        progressBar.ariaValueNow = `${(fileUploadTotal / fileTotal) * 100}`;
        progressBar.innerHTML = `${fileUploadTotal} / ${fileTotal}`;
    }

    async function showNextDialog() {
        if (dialogQueue.length > 0 && !dialogIsOpen) {
            dialogIsOpen = true;
            let { type, dialogOptions, fileData } = dialogQueue.shift();
            let result = await Swal.fire(dialogOptions);
            if (result.isConfirmed && type === 'upload') {
                let response = await fetch('/administration/upload', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(fileData)
                });
                let status = response.status;
                if (status === 200) {
                    fileUploadTotal++;
                    updateProgressBar();
                }
            }
            else if (type === 'upload') {
                fileTotal--;
                updateProgressBar();
            }
            dialogIsOpen = false;
            showNextDialog();
        }
    }

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
    const modalExistingFoldersDelete = document.querySelector('#existingFolderDelete');
    folders.forEach((folder) => {
        modalParentFolders.forEach((select) => {
            select.innerHTML += `<option value="${folder.dataset.folder}">${folder.dataset.name}</option>`;
        });
        modalExistingFolders.innerHTML += `<option value="${folder.dataset.folder}">${folder.dataset.name}</option>`;
        modalExistingFoldersDelete.innerHTML += `<option value="${folder.dataset.folder}">${folder.dataset.name}</option>`;
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
            modifyFolderModal.querySelector('#folderPriority').value = '';
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
        modifyFolderModal.querySelector('#folderPriority').value = folder.dataset.priority;
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
        let folderPriority = addFolderModal.querySelector('#folderPriority').value;
        let folderColor = addFolderModal.querySelector('#folderColor').value;
        createFolderButton.disabled = true;
        if (folderName !== '' && folderPriority !== '') {
            socket.emit('create_folder', { folderName: folderName, parentFolderId: parentFolderId, folderRoles: folderRoles, folderPriority: folderPriority, folderColor: folderColor });
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
        alert(`La création du classeur a échoué: ${data.error}`);
        createFolderButton.disabled = false;
    });

    const formCreateFolder = document.querySelector('#addFolderModal').querySelector('form');
    formCreateFolder.addEventListener('submit', function (event) {
        if (fileTotal != fileUploadTotal) {
            event.preventDefault();
            alert('Veuillez attendre la fin du téléversement des fichiers avant de créer un classeur.');
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
        let folderPriority = modifyFolderModal.querySelector('#folderPriority').value;
        let folderColor = modifyFolderModal.querySelector('#folderColor').value;
        modifyFolderButton.disabled = true;
        if (folderName !== '' && folderId !== '0' && folderPriority !== '') {
            socket.emit('modify_folder', { folderId: folderId, folderName: folderName, parentFolderId: parentFolderId, folderRoles: folderRoles, folderPriority: folderPriority, folderColor: folderColor });
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
        alert(`La modification du classeur a échoué: ${data.error}`);
        modifyFolderButton.disabled = false;
    });

    const formModifyFolder = document.querySelector('#modifyFolderModal').querySelector('form');
    formModifyFolder.addEventListener('submit', function (event) {
        if (fileTotal != fileUploadTotal) {
            event.preventDefault();
            alert('Veuillez attendre la fin du téléversement des fichiers avant de modifier un classeur.');
            return;
        }
    });

    const deleteFolderModal = document.querySelector('#deleteFolderModal');
    const deleteFolderButton = document.querySelector('#deleteFolderButton');
    deleteFolderButton.addEventListener('click', function (event) {
        event.preventDefault();
        if (fileTotal != fileUploadTotal) {
            return;
        }
        let folderId = deleteFolderModal.querySelector('#existingFolderDelete').value;
        if (folderId !== '0') {
            socket.emit('delete_folder', { folderId: folderId });
        }
        else {
            alert('Veuillez sélectionner un classeur.');
        }
    });

    socket.on('folder_deleted', function (data) {
        window.location.reload();
    });

    socket.on('folder_not_deleted', function (data) {
        alert(`La suppression du classeur a échoué: ${data.error}`);
    });

    const formDeleteFolder = document.querySelector('#deleteFolderModal').querySelector('form');
    formDeleteFolder.addEventListener('submit', function (event) {
        if (fileTotal != fileUploadTotal) {
            event.preventDefault();
            alert('Veuillez attendre la fin du téléversement des fichiers avant de supprimer un classeur.');
            return;
        }
    });

    let isFolderChecked = false;
    const actionsDropdown = document.querySelector('#actionsDropdown');
    const folderCheckboxes = document.querySelectorAll('.folder-checkbox');
    folderCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener('change', function (event) {
            let folderId = event.target.dataset.folder;
            let subfolders = document.querySelectorAll(`.folder-${folderId} .folder-checkbox`);
            let files = document.querySelectorAll(`.folder-${folderId} .file-checkbox`);
            subfolders.forEach((subfolder) => {
                if (subfolder !== checkbox) {
                    subfolder.checked = event.target.checked;
                    subfolder.disabled = event.target.checked;
                }
                let subfolderId = subfolder.dataset.folder;
                let subfolderFiles = document.querySelectorAll(`.folder-${subfolderId} .file-checkbox`);
                subfolderFiles.forEach((file) => {
                    file.checked = event.target.checked;
                    file.disabled = event.target.checked;
                });
            });
            files.forEach((file) => {
                file.checked = event.target.checked;
                file.disabled = event.target.checked;
            });
            isFolderChecked = Array.from(folderCheckboxes).some(cb => cb.checked);
            if (isFolderChecked) {
                actionsDropdown.classList.remove('d-none');
                if (!document.querySelector('#actionArchive')) {
                    actionsDropdown.querySelector('ul').insertAdjacentHTML('beforeend', '<li class="dropdown-item text-dark" id="actionArchive" style="cursor: pointer;">Archiver le/les classeur(s) sélectionné(s)</li>');
                    if (document.querySelector('#actionDelete')) {
                        actionsDropdown.querySelector('ul').removeChild(document.querySelector('#actionDelete'));
                    }
                    actionsDropdown.querySelector('#actionArchive').addEventListener('click', async function (event) {
                        let folders = Array.from(folderCheckboxes).filter(cb => cb.checked);
                        let files = Array.from(filesCheckboxes).filter(cb => cb.checked);
                        let folderIds = folders.map(cb => cb.dataset.folder);
                        let fileIds = files.map(cb => cb.dataset.file);
                        let folderFiles = [];
                        for (let folderId of folderIds) {
                            folderFiles.push(Array.from(document.querySelectorAll(`.folder-${folderId} .file-checkbox:checked`)).map(cb => cb.dataset.file));
                        }
                        let allFiles = [];
                        folderFiles.forEach((files) => {
                            allFiles.push(...files);
                        });
                        let folderFilesIds = Array.from(new Set(allFiles));
                        if (folderFilesIds.length === fileIds.length) {
                            if (fileTotal === fileUploadTotal) {
                                let confirmation = confirm('Voulez-vous vraiment archiver le/les classeurs(s) sélectionné(s) ?');
                                if (confirmation) {
                                    socket.emit('archive_folders', { folderIds: folderIds });
                                }
                            }
                            else {
                                alert('Veuillez attendre la fin du téléversement des fichiers avant d\'archiver un classeur.');
                            }
                        }
                        else {
                            alert('Les fichiers sélectionnés ne sont pas tous dans les classeurs sélectionnés.');
                        }
                    });
                }
            }
            else {
                actionsDropdown.classList.add('d-none');
                actionsDropdown.querySelector('ul').removeChild(document.querySelector('#actionArchive'));
            }
        });
    });

    const filesCheckboxes = document.querySelectorAll('.file-checkbox');
    filesCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener('change', function (event) {
            let folderId = event.target.dataset.folder;
            let files = document.querySelectorAll(`.folder-${folderId} .file-checkbox`);
            let filesChecked = Array.from(files).filter(cb => cb.checked);
            if (filesChecked.length > 0) {
                actionsDropdown.classList.remove('d-none');
                if (!document.querySelector('#actionDelete') && !isFolderChecked) {
                    actionsDropdown.querySelector('ul').insertAdjacentHTML('beforeend', '<li class="dropdown-item text-dark" id="actionDelete" style="cursor: pointer;">Supprimer le/les fichier(s) sélectionné(s)</li>');
                    actionsDropdown.querySelector('#actionDelete').addEventListener('click', async function (event) {
                        let files = Array.from(filesCheckboxes).filter(cb => cb.checked);
                        let fileIds = files.map(cb => cb.dataset.file);
                        if (fileTotal === fileUploadTotal) {
                            let confirmation = confirm('Voulez-vous vraiment supprimer le/les fichier(s) sélectionné(s) ?');
                            if (confirmation) {
                                socket.emit('delete_files', { fileIds: fileIds });
                            }
                        }
                        else {
                            alert('Veuillez attendre la fin du téléversement des fichiers avant de supprimer un fichier.');
                        }
                    });
                }
            }
        });
    });

    actionsDropdown.querySelector('#actionDownload').addEventListener('click', function (event) {
        let files = Array.from(filesCheckboxes).filter(cb => cb.checked);
        let fileIds = files.map(cb => cb.dataset.file);
        if (fileIds.length > 0) {
            let confirmation = confirm('Voulez-vous vraiment télécharger le/les fichier(s) sélectionné(s) ?');
            if (confirmation) {
                fetch('/download/archive', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ fileIds: fileIds })
                }).then(response => {
                    if (response.ok) {
                        response.blob().then(blob => {
                            let url = window.URL.createObjectURL(blob);
                            let a = document.createElement('a');
                            a.href = url;
                            a.download = 'archive.zip';
                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(url);
                        });
                    }
                });
            }
        }
    });

    socket.on('folders_archived', function (data) {
        window.location.reload();
    });

    socket.on('folders_not_archived', function (data) {
        alert('L\'archivage des classeurs a échoué.');
    });

    socket.on('files_deleted', function (data) {
        window.location.reload();
    });

    socket.on('files_not_deleted', function (data) {
        alert('La suppression des fichiers a échoué.');
    });
});