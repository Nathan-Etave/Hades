let previewModal;
export function previewAfterRender() {
    if (!previewModal) {
        previewModal = new bootstrap.Modal(document.querySelector('#previewModal'));
    }
    const files = document.querySelectorAll('#file');
    files.forEach((file) => {
        file.addEventListener('click', async function (event) {
            let target = event.target;
            if (event.target.nodeName === 'P' || event.target.nodeName === 'I' || event.target.nodeName === 'SPAN') {
                target = event.target.parentElement.parentElement;
            }
            if (event.target.className.includes('desktop-element')) {
                target = event.target.parentElement;
            }
            const fileId = target.dataset.file;
            const folderId = target.dataset.folder;
            const fileType = target.dataset.type;
            let previewModalLabel = document.querySelector('#previewModalLabel');
            previewModalLabel.innerHTML = target.querySelector('p').textContent;
            const modalBody = document.querySelector('#previewModal').querySelector('.modal-body');
            modalBody.innerHTML = '';

            switch (fileType) {
                case 'pdf':
                case 'jpg':
                case 'jpeg':
                case 'png':
                case 'gif':
                case 'svg':
                case 'bmp':
                case 'tiff':
                case 'webp':
                case 'mp4':
                case 'webm':
                case 'ogg':
                case 'mp3':
                case 'wav':
                case 'aac':
                case 'txt':
                    const iframe = iframeElement(fileId, folderId);
                    modalBody.appendChild(iframe);
                    break;
                case 'xlsx':
                case 'xls':
                case 'csv':
                case 'ods':
                    const [tabs, content] = await spreadsheetElement(fileId, folderId);
                    modalBody.appendChild(tabs);
                    modalBody.appendChild(content);
                    break;
                case 'docx':
                    const mammoth = await docxElement(fileId, folderId);
                    modalBody.appendChild(mammoth);
                    break;
                default:
                    const element = defaultElement();
                    modalBody.appendChild(element);
                    break;
            }
            previewModal.show();
        });
    });

    function iframeElement(fileId, folderId) {
        const iframe = document.createElement('iframe');
        iframe.src = `/classeur/${folderId}/fichier/${fileId}`;
        iframe.width = '100%';
        iframe.height = '100%';
        return iframe;
    }

    function defaultElement() {
        const p = document.createElement('p');
        p.innerHTML = 'Aucune prévisualisation disponible.';
        return p;
    }

    async function docxElement(fileId, folderId) {
        const url = `/classeur/${folderId}/fichier/${fileId}`;
        const data = await (await fetch(url)).arrayBuffer();
        const result = await mammoth.convertToHtml({ arrayBuffer: new Uint8Array(data) });
        const div = document.createElement('div');
        div.innerHTML = result.value;
        return div;
    }

    async function spreadsheetElement(fileId, folderId) {
        const url = `/classeur/${folderId}/fichier/${fileId}`;
        const data = await (await fetch(url)).arrayBuffer();
        const workbook = XLSX.read(new Uint8Array(data), { type: 'array', cellStyles: true });

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

            const worksheet = workbook.Sheets[sheetName];
            const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

            const table = document.createElement('table');
            table.className = 'spreadsheet-table';

            jsonData.forEach((row, rowIndex) => {
                const tr = document.createElement('tr');

                row.forEach((cell, cellIndex) => {
                    const td = document.createElement(rowIndex === 0 ? 'th' : 'td');
                    td.textContent = cell;

                    const cellRef = XLSX.utils.encode_cell({ r: rowIndex, c: cellIndex });
                    const cellObj = worksheet[cellRef];
                    if (cellObj && cellObj.s) {
                        const cssStyle = convertExcelStyleToCSS(cellObj.s);
                        td.style.cssText = cssStyle;
                    }

                    tr.appendChild(td);
                });

                table.appendChild(tr);
            });

            divTab.appendChild(table);
            div.appendChild(divTab);
        });

        return [ul, div];
    }

    function convertExcelStyleToCSS(style) {
        let css = '';
        if (style.patternType === 'solid') {
            if (style.fgColor && style.fgColor.rgb) {
                css += `background-color: #${style.fgColor.rgb}; `;
            }
        }
        return css;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    previewAfterRender();
});