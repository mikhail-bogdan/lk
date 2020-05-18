function onClick(argument) {
    element = argument.parentElement.getElementsByClassName("desc")[0];
    if (element.style.display === "none") {
        element.style.display = "block"
        argument.innerHTML = "<i>Скрыть описание</i>"
    }
    else {
        element.style.display = "none"
        argument.innerHTML = "<i>Показать описание</i>"
    }
}