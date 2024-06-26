document.addEventListener('DOMContentLoaded', function () {

    let reactivationButton = document.getElementById("btn_reactivation") || { addEventListener: () => {} };

    // handle the reactivation button
    reactivationButton.addEventListener('click', async function () {
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
            .then(async response => {
                if (response.status === 200) { // success
                    await createAlertMessage("La demande de réactivation a bien été envoyée ! \n vous recevrez un mail lorsqu'elle sera traitée.", "success");
                    window.location.href = "/connexion";
                }
                if (response.status === 404) { // error
                    if (response.body.error === "user not found") {
                        await createAlertMessage("Aucun utilisateur n'est associé à cet email.", "warning");
                    }
                    else if (response.body.error === "user already have a notification") {
                        await createAlertMessage("Vous avez déjà une demande de réactivation en cours.", "warning");
                    }
                    else {
                        await createAlertMessage("Une erreur est survenue.", "error");
                    }
                    window.location.href = "/connexion";
                }
            })
    });

    async function createAlertMessage(message, type) {
        await Swal.fire({
            icon: type,
            title: message,
            showConfirmButton: true,
            backdrop: false
        });
    }
});