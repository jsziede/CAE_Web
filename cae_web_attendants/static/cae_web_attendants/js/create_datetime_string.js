//converts the values from a date input and a time input into a django datetime string
let createDatetimeString = function(datetimeInputId) {
    let dateInput = document.getElementById("dateInput");
    let timeInput = document.getElementById("timeInput");
    
    let datetimeInput = document.getElementById(datetimeInputId.toString());

    if (dateInput.value != "" && timeInput.value != "") {
        datetimeInput.value = dateInput.value + " " + timeInput.value;
    }
}