document.addEventListener('DOMContentLoaded', function() {
    var sidenav = document.getElementById("sidenav");
    var button = document.getElementById("button");
    button.onclick = manageNav;
    function manageNav() {
        if (sidenav.classList.contains("active")) {
            sidenav.classList.remove("active");
        } else {
            sidenav.classList.add("active");
        }
    }
    let notification_enabled = document.querySelector(".notification_enabler").textContent;
    let svg_notifications = document.querySelectorAll(".logo_notification g");
    Array.from(svg_notifications).forEach(function(element) {
        if (notification_enabled == "False") {
            element.style.animation = "none";
        }
    });
});