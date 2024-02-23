document.addEventListener('DOMContentLoaded', function() { 
    let acceptButtons = document.querySelectorAll('.ok');
    acceptButtons.forEach(function(button) {
        let id = button.id;
        let role = document.getElementById('role'+id).value;
        let  userId = button.getAttribute('user-id');
        button.addEventListener('click', function(event) {
            event.preventDefault();
            fetch('/utilisateurAccepter', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: id,
                    role: role,
                    userId: userId
                })
            })
            .then(response => {
                document.getElementById('notification'+id).remove();
            })
        });
    });

    let refuseButtons = document.querySelectorAll('.non');
    refuseButtons.forEach(function(button) {
        let id = button.getAttribute('data-notification');
        let userId = button.getAttribute('user-id');
        button.addEventListener('click', function(event) {
            event.preventDefault();
            fetch('/utilisateurRefuser', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: id,
                    userId: userId
                })
            })
            .then(response => {
                document.getElementById('notification'+id).remove();
            })
        });
    });
});