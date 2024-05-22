// Function to display the number of files in the desktop icon
export function baseAfterRender(number) {
    let numberIcon = document.getElementById('number');

    if (numberIcon) {
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
}

// Handle the création of the desktop list in the localStorage
document.addEventListener('DOMContentLoaded', function () {
    let deskList = JSON.parse(localStorage.getItem('desktop'));
    if (deskList === null) {
        deskList = [];
        localStorage.setItem('desktop', JSON.stringify(deskList));
    }
    baseAfterRender(deskList.length);
});

const burger = document.querySelector('.fa-bars');
const nav = document.querySelector('.navbar');
const logoText = document.querySelector('.logo-text');
const navItems = document.querySelector('.nav-items');
const navLinks = document.querySelectorAll('.nav-items > li > a');
const xMark = document.querySelector('.fa-xmark');

function setBurgerStyles() {
    logoText.style.setProperty('display', 'none', 'important');
    burger.style.setProperty('display', 'none', 'important');
    nav.style.setProperty('display', 'flex', 'important');
    nav.style.setProperty('margin-left', '0', 'important');
    navItems.style.setProperty('padding-left', '0', 'important');
    navLinks.forEach(link => {
        link.style.setProperty('margin', '0.5rem', 'important');
        link.parentElement.style.setProperty('margin', '0', 'important');
    });
    xMark.style.setProperty('display', 'block', 'important');
}

function setXMarkStyles() {
    logoText.style.setProperty('display', 'block', 'important');
    burger.style.setProperty('display', 'block', 'important');
    nav.style.setProperty('display', 'none', 'important');
    nav.style.setProperty('margin-left', 'auto', 'important');
    navItems.style.setProperty('padding-left', 'auto', 'important');
    navLinks.forEach(link => {
        link.style.setProperty('margin', '0', 'important');
        link.parentElement.style.setProperty('margin', '0', 'important');
    });
    xMark.style.setProperty('display', 'none', 'important');
}

function resetStyles() {
    logoText.style.removeProperty('display');
    burger.style.removeProperty('display');
    nav.style.removeProperty('display');
    nav.style.removeProperty('margin-left');
    navItems.style.removeProperty('padding-left');
    navLinks.forEach(link => {
        link.style.removeProperty('margin');
        link.parentElement.style.removeProperty('margin');
    });
    xMark.style.removeProperty('display');
}

burger.addEventListener('click', setBurgerStyles);
xMark.addEventListener('click', setXMarkStyles);

window.addEventListener('resize', () => {
    if (window.innerWidth > 1050) {
        resetStyles();
    }
});