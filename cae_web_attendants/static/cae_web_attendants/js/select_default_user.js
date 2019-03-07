let selectDefaultUser = function(userId) {
    let employees = document.getElementById("id_employee");
    for (i = 0; i < employees.options.length; i++) {
        if (employees.options[i].innerText == userId) {
            employees.options[i].selected = true;
            i = employees.options.length;
        }
    }
}