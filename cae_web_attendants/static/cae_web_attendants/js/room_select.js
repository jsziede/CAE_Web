let roomInput = document.getElementById(roomInputId);

let roomSelect = function(roomId) {
    roomId = roomId.toString();
    console.log(roomId);
    let selected = document.getElementsByClassName("selected-room");
    while (selected.length) {
        selected[0].classList.remove("selected-room");
    }

    let selectedRoom = document.getElementById(roomId);
    roomInput.value = roomId;
    selectedRoom.classList.add("selected-room");
}