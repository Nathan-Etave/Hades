document.addEventListener('DOMContentLoaded', function () {

    let reactivationButton = document.getElementById("btn_reactivation");

    // handle the reactivation button
    reactivationButton.addEventListener('click', function () {
        let email_user = document.getElementById("email").value;
        let csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        fetch("/connexion/notification", {
            method: "POST",
            body: JSON.stringify({
                "type": 2,
                "email_user": email_user,
            }),
            headers: {
                "Content-Type": "application/json",
                'X-CSRFToken': csrfToken
            }
        })
            .then(response => response.json().then(data => ({ status: response.status, body: data })))
            .then(response => {
                if (response.status === 200) { // success
                    createAlertMessage("La demande de réactivation a bien été envoyée ! \n vous recevrez un mail lorsqu'elle sera traitée.", "success");
                    window.location.href = "/connexion";
                }
                if (response.status === 404) { // error
                    if (response.body.error === "user not found") {
                        createAlertMessage("Aucun utilisateur n'est associé à cet email.", "warning");
                    }
                    else if (response.body.error === "user already have a notification") {
                        createAlertMessage("Vous avez déjà une demande de réactivation en cours.", "warning");
                    }
                    else {
                        createAlertMessage("Une erreur est survenue.", "error");
                    }
                    window.location.href = "/connexion";
                }
            })
    });

    function createAlertMessage(message, type) {
        Swal.fire({
            position: 'top-end',
            icon: type,
            title: message,
            showConfirmButton: true,
            timer: 2000,
            backdrop: false
        });
    }
});