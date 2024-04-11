document.addEventListener('DOMContentLoaded', function() {

    let btn_and = document.getElementById("btn_and");
    let btn_or = document.getElementById("btn_or");
    let search_bar = document.getElementById("search");

    btn_and.addEventListener('click', function() {
        search_bar.value += " & ";
    });

    btn_or.addEventListener('click', function() {
        search_bar.value += " | "
    });
});