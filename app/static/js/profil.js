document.addEventListener('DOMContentLoaded', function () {
    let btnVerif = document.getElementById("btn_verif");
    let csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    btnVerif.addEventListener('click', function () {
        console.log("OK")
        let verifPassword = document.getElementById("verif_password");
        password = verifPassword.value
        fetch('verification', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                "password": password
            })
        })
            .then(response => response.json())
            .then(response => {
                console.log(response.verif)
                if (response.verif) {
                    window.location.href = "edit";
                }
                else {
                    let alertMdp = document.getElementById("alert_mdp");
                    alertMdp.classList.remove("d-none")
                }
            })
    });

    let btnLogout = document.getElementById("logout");
    btnLogout.addEventListener('click', function () {
        fetch('deconnexion', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                'X-CSRFToken': csrfToken
            }
        })
            .then(response => response.json())
            .then(response => {
                if (response.status === "success") {
                    window.location.href = "/connexion";
                }
                else {
                    alert("Erreur lors de la déconnexion");
                }
            })
    });
});