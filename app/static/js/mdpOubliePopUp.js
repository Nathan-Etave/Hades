document.addEventListener('DOMContentLoaded', function() {
    let button = document.getElementById('mdp_oublie_button');
    let button2 = document.getElementById('mdp_oublie_button2');
    let pop_up = document.getElementById('mdp_oublie_hidden');
    button.addEventListener('click', function() {
        pop_up.classList.toggle('mdp_oublie_hidden');
        pop_up.classList.toggle('mdp_oublie');
    });
    button2.addEventListener('click', function() {
        pop_up.classList.toggle('mdp_oublie_hidden');
        pop_up.classList.toggle('mdp_oublie');
    });
    
});