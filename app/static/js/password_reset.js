export function eyeButtonsAfterRender() {
    let eyeButtons = document.querySelectorAll('.toggle-password');
    eyeButtons.forEach((eyeButton) => {
        eyeButton.addEventListener('click', function (event) {
            const passwordInput = eyeButton.parentElement.parentElement.querySelector('input');
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                eyeButton.classList.remove('fa-eye-slash');
                eyeButton.classList.add('fa-eye');
            }
            else {
                passwordInput.type = 'password';
                eyeButton.classList.remove('fa-eye');
                eyeButton.classList.add('fa-eye-slash');
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', function () {
    eyeButtonsAfterRender();
});