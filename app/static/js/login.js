document.addEventListener('DOMContentLoaded', function () {

    let reactivationButton = document.getElementById("btn_reactivation");

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
                if (response.status === 200) {
                    alert("La demande de réactivation a bien été envoyée ! \n vous recevrez un mail lorsqu'elle sera traitée.");
                    window.location.href = "/connexion";
                }
                if (response.status === 404) {
                    if (response.body.error === "user not found") {
                        alert("Aucun utilisateur n'est associé à cet email.");
                    }
                    else if (response.body.error === "user already have a notification") {
                        alert("Vous avez déjà une demande de réactivation en cours.");
                    }
                    else {
                        alert("Une erreur est survenue.");
                    }
                    window.location.href = "/connexion";
                }
            })
    });

});