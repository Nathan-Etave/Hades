export function baseAfterRender(number) {
    let numberIcon = document.getElementById('number');

    if (number === 0) {
        numberIcon.style.display = 'none';
    }
    else if (number < 10) {
        numberIcon.style.display = 'flex';
        numberIcon.innerHTML = number;
    }
    else {
        numberIcon.style.display = 'flex';
        numberIcon.innerHTML = '9+';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    let deskList = JSON.parse(localStorage.getItem('desktop'));
    if (deskList === null) {
        deskList = [];
        localStorage.setItem('desktop', JSON.stringify(deskList));
    }
    baseAfterRender(deskList.length);
});