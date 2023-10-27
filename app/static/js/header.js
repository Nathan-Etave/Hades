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
});