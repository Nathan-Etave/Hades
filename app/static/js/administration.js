document.addEventListener('DOMContentLoaded', function () {
    let progressBar = document.querySelector('.progress-bar');
    let fileInput = document.querySelectorAll('.file-input');
    let fileTotal = 0
    let fileUploadTotal = 0
    let csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    fileInput.forEach((input) => {
        input.addEventListener('change', async function (event) {
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
                                data: ev.target.result
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
    window.onbeforeunload = function () {
        return '';
    };
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
    });
    
    socket.on('file_deletion_failed', function (data) {
        alert('La suppression du fichier a échoué');
    });

    const folders = document.querySelectorAll('#folder');
    const searchBars = [];
    const intialFiles = {};
    folders.forEach((folder) => {
        searchBars.push(folder.querySelector('#fileSearch'));
        intialFiles[folder.dataset.folder] = folder.querySelector(`#filesAccordion${folder.dataset.folder}`).children;
    });
    searchBars.forEach((searchBar) => {
        searchBar.addEventListener('input', function (event) {
            if (event.target.value === '') {
                Array.from(intialFiles[event.target.dataset.folder]).forEach((file) => {
                    file.style.display = 'block';
                });
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
    });
});