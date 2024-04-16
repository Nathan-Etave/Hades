document.addEventListener('DOMContentLoaded', function() { 
    let btnVerif = document.getElementById("btn_verif");
    let csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    btnVerif.addEventListener('click', function() {
        console.log("OK")
        let verifPassword = document.getElementById("verif_password");
        password = verifPassword.value
        fetch('verification', {
            method : "POST",
            headers: {
                "Content-Type": "application/json",
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                "password" : password
            })
        })
        .then(response => response.json())
        .then(response => {
            console.log(response.verif)
            if (response.verif) {
                let profil = document.getElementById("profil");
                let profilEdit = document.getElementById("profil_edit");
                profil.classList.add("d-none");
                profilEdit.classList.remove("d-none");
                
                let closeBtn = document.getElementById("close");
                closeBtn.click();
            }
            else {
                let alertMdp = document.getElementById("alert_mdp");
                alertMdp.classList.remove("d-none")
            }
        })
    });
});