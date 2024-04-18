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

    const previewModal = new bootstrap.Modal(document.querySelector('#previewModal'));
    const files = document.querySelectorAll('#file');
    files.forEach((file) => {
        file.addEventListener('click', async function (event) {
            target = event.target;
            if (event.target.nodeName === 'P' || event.target.nodeName === 'I') {
                target = event.target.parentElement.parentElement;
            }
            const fileId = target.dataset.file;
            const folderId = target.dataset.folder;
            const fileType = target.dataset.type;
            let previewModalLabel = document.querySelector('#previewModalLabel');
            previewModalLabel.innerHTML = target.innerHTML;
            const modalBody = document.querySelector('#previewModal').querySelector('.modal-body');
            modalBody.innerHTML = '';

            switch (fileType) {
                case 'pdf':
                case 'jpg':
                case 'jpeg':
                case 'png':
                case 'gif':
                case 'svg':
                    const element = iframeElement(fileId, folderId);
                    modalBody.appendChild(element);
                    break;
                case 'xlsx':
                case 'xls':
                case 'csv':
                case 'ods':
                case 'txt':
                    const [tabs, content] = await spreadsheetElement(fileId, folderId);
                    modalBody.appendChild(tabs);
                    modalBody.appendChild(content);
                    break;
                default:
                    element = defaultElement();
                    break;
            }
            previewModal.show();
        });
    });

    function iframeElement(fileId, folderId) {
        const iframe = document.createElement('iframe');
        iframe.src = `/dossier/${folderId}/fichier/${fileId}`;
        iframe.width = '100%';
        iframe.height = '100%';
        return iframe;
    }

    function defaultElement() {
        const p = document.createElement('p');
        p.innerHTML = 'Aucune prévisualisation disponible.';
        return p;
    }

    async function spreadsheetElement(fileId, folderId) {
        const url = `/dossier/${folderId}/fichier/${fileId}`;
        const data = await (await fetch(url)).arrayBuffer();
        const workbook = XLSX.read(new Uint8Array(data), {type: 'array'});
    
        const div = document.createElement('div');
        div.className = 'tab-content';
    
        const ul = document.createElement('ul');
        ul.className = 'nav nav-tabs';
    
        workbook.SheetNames.forEach((sheetName, index) => {
            const li = document.createElement('li');
            li.className = 'nav-item';
            const a = document.createElement('a');
            a.className = 'nav-link' + (index === 0 ? ' active' : '');
            a.id = `tab-${index}`;
            a.setAttribute('data-bs-toggle', 'tab');
            a.setAttribute('href', `#content-${index}`);
            a.textContent = sheetName;
            li.appendChild(a);
            ul.appendChild(li);
    
            const divTab = document.createElement('div');
            divTab.className = 'tab-pane fade' + (index === 0 ? ' show active' : '') + ' spreadsheet-table';
            divTab.id = `content-${index}`;
            divTab.innerHTML = XLSX.utils.sheet_to_html(workbook.Sheets[sheetName]);
            div.appendChild(divTab);
        });
        return [ul, div];
    }
});