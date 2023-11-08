let buttons = document.getElementsByClassName("not_selected");

for (let button of buttons) {
    button.onclick = function() {
        let fileIndex = button.querySelector('span').textContent;
        fetch('multivue_redirect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                file_index: fileIndex
            })
        });
    }
}
