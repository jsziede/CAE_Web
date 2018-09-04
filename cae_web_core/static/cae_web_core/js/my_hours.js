/**
 * Core JavaScript logic for my_hours page.
 */


 // Wait for full page load.
$(document).ready(function() {
    console.log(shifts);

    // Grab DOM elements.
    var shift_submit_button = $('#shift-submit');
    console.log(shift_submit_button);

    // Create socket connection.
    var socket = new WebSocket('ws://' + domain + '/ws/caeweb/employee/my_hours/');

    // Handling for early socket termination.
    socket.onClose = function(event) {
        console.error('Socket closed unexpectedly');
    };

    // Handle incomming socket message event.
    socket.onmessage = function(message) {
        var data = JSON.parse(message.data);
        json_shifts = JSON.parse(data.json_shifts);
        last_shift = json_shifts[json_shifts.length - 1];
    };

    // Handle button click.
    shift_submit_button.on('click', function(event) {
        console.log('Shift submit clicked.');
        socket.send(JSON.stringify({
            'shift_submit': true,
        }));
    });
});
