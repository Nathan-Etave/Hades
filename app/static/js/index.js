document.addEventListener('DOMContentLoaded', function() {
    let multiview_cookie = document.cookie.match(/multiview_list="([^"]*)"/)[1].split('\\073');

    let starButtons = document.querySelectorAll('.etoile');
    starButtons.forEach(function(button) {
        let id = button.id;
        button.addEventListener('click', function(event) {
            if(button.className === 'etoile_vide'){
                event.preventDefault();
                fetch('/favorize', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        id: id
                    })
                })
                .then( response => {
                    console.log(response.status);
                    button.src = '/static/img/etoile_pleine.png';
                    button.className = 'etoile';
                });
            }
            else{
                event.preventDefault();
                fetch('/unfavorize', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        id: id
                    })
                })
                .then( response => {
                    button.src = '/static/img/etoile_vide.png';
                    button.className = 'etoile_vide';
            });}
        });
    });

    let multiviewButtons = document.querySelectorAll('.multiview');
    multiviewButtons.forEach(function(button) {
        let id = button.id;
        id = id.split(' ')[1];
        if(multiview_cookie.includes(id)){
            button.src = '/static/img/etoile_pleine.png';
        }
    });
});