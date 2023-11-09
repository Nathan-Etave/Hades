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
    let svg_notification = document.querySelector(".logo_notification g");
    if (notification_enabled == "False") {
      svg_notification.style.animation = "none";
    }
  });