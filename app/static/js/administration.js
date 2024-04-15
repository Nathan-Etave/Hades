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
    window.onbeforeunload = function() {
        return '';
     };
});