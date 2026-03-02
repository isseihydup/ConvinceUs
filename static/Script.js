const socket = io();

function enter(){
    document.getElementById("intro").style.display="none";
    document.getElementById("menu").style.display="block";
}

function createRoom(){
    socket.emit("create_room");
}

socket.on("room_created", room=>{
    document.getElementById("room").value = room;
    alert("Room Code: " + room);
});

function joinRoom(){
    const name = document.getElementById("name").value;
    const room = document.getElementById("room").value;
    socket.emit("join_room",{name, room});
    document.getElementById("menu").style.display="none";
    document.getElementById("game").style.display="block";
    document.getElementById("roomDisplay").innerText="Room: "+room;
}

socket.on("player_joined", name=>{
    const div = document.getElementById("players");
    div.innerHTML += "<p>"+name+"</p>";
});

function startGame(){
    const room = document.getElementById("room").value;
    socket.emit("start_game", room);
}

socket.on("game_started", data=>{
    const name = document.getElementById("name").value;
    const role = data.roles[name];
    document.getElementById("role").innerHTML =
        "<h3>Your Role: "+role+"</h3>" +
        (role === "Crew" ? "<p>Topic: "+data.topic+"</p>" : "<p>Unknown Topic</p>");
});

function vote(player){
    const room = document.getElementById("room").value;
    socket.emit("vote",{room, target:player});
}

socket.on("vote_update", data=>{
    alert("Vote cast for "+data.target);
});
