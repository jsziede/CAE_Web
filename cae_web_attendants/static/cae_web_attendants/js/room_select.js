//Uses the id of a div to store it into the hidden room input from the form.
//The id is passed as an argument using the onclick event from the web page.

//roomInputId is the id that is passed as an argument
let roomInput = document.getElementById(roomInputId);

let roomSelect = function(roomId) {
    //saves the id as a string
    roomId = roomId.toString();

    //gets all elements with the .selected class and removes the class
    //this occurs because a new element was selected
    let selected = document.getElementsByClassName("selected-room");
    while (selected.length) {
        selected[0].classList.remove("selected-room");
    }

    //add the .selected class to the newly selected element
    //the newly selected element is the div with the id that was passed as an argument
    let selectedRoom = document.getElementById(roomId);
    roomInput.value = roomId;
    selectedRoom.classList.add("selected-room");
}
