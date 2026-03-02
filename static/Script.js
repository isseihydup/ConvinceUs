const socket = io();
let currentRoom = "";
let playerName = "";

function createRoom(){
    socket.emit("create_room");
}

socket.on("room_created", room=>{
    document.getElementById("room").value = room;
    alert("Room Code: " + room);
});

function joinRoom(){
    playerName = document.getElementById("name").value;
    currentRoom = document.getElementById("room").value;

    socket.emit("join_room",{name:playerName, room:currentRoom});
    document.getElementById("menu").style.display="none";
    document.getElementById("game").style.display="block";
    document.getElementById("roomDisplay").innerText="Room: "+currentRoom;
}

socket.on("player_joined", name=>{
    document.getElementById("players").innerHTML +=
        `<button onclick="vote('${name}')">${name}</button>`;
});

function startGame(){
    socket.emit("start_game", currentRoom);
}

function vote(target){
    socket.emit("vote",{
        room:currentRoom,
        voter:playerName,
        target:target
    });
}

socket.on("eliminated", data=>{
    document.getElementById("status").innerHTML =
        `ELIMINATED: ${data.player}<br>ROLE: ${data.role}`;
});
