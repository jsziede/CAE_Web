//loops through all the employee names and compares each to the currently logged in user to find a match.
//if a match is found, it becomes the default value of the employee input for the room checkout field.
let selectDefaultUser = function(userId) {
    let employees = document.getElementById("id_employee");
    for (i = 0; i < employees.options.length; i++) {
        if (employees.options[i].innerText == userId) {
            employees.options[i].selected = true;
            i = employees.options.length;
        }
    }
}
