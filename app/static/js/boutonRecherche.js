document.addEventListener('DOMContentLoaded', function() {
    let button2 = document.getElementById('buttonRecherche2');
    let button3 = document.getElementById('buttonRecherche3');
    let barreRecherche = document.getElementById('barreRecherche');
    let cursorPosition = 0;

    barreRecherche.addEventListener('keydown', e => {
        cursorPosition = e.target.selectionStart+1;
    })

    barreRecherche.addEventListener('click', e => {
        cursorPosition = e.target.selectionStart+1;
    })

    button2.addEventListener('click', function() {
        barreRecherche.value = barreRecherche.value.slice(0,cursorPosition) + ' & ' + barreRecherche.value.slice(cursorPosition);
        barreRecherche.focus();
        barreRecherche.setSelectionRange(cursorPosition+3, cursorPosition+3)
        cursorPosition+=3;
    })

    button3.addEventListener('click', function() {
        barreRecherche.value = barreRecherche.value.slice(0,cursorPosition) + ' | ' + barreRecherche.value.slice(cursorPosition);
        barreRecherche.focus();
        barreRecherche.setSelectionRange(cursorPosition+3, cursorPosition+3)
        cursorPosition+=3;
    })

    let infoBox = document.getElementById('infoBox');
    let infoButton = document.getElementById('infoButton');
    infoButton.addEventListener('mouseover', function() {
        infoBox.classList.add('infoBoxOpened');
        infoBox.classList.remove('infoBoxClosed');

    })
    infoButton.addEventListener('mouseout', function() {
        infoBox.classList.add('infoBoxClosed');
        infoBox.classList.remove('infoBoxOpened');

    })
});