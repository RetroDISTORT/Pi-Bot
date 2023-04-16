
let ws;

function sendToServer(data) {
    if (!ws){
	console.log("No Websocket connection")
	init()
	return;
    }

    if (ws.readyState)
	ws.send(data);
}


function init() {
    if (ws) {
	ws.onerror = ws.onopen = ws.onclose = null;
	ws.close();
	document.getElementById("sendButton").disabled = true;
    }

    wsAddress    = 'ws://' + serverIP + ':' + websocketPort;
    ws           = new WebSocket(wsAddress);//, { rejectUnauthorized: false });
    ws.onopen    = () => { document.getElementById("sendButton").disabled = false; };
    ws.onmessage = ({ data }) => showMessage(data);//showMessage(data);
    ws.onclose   = function() { ws = null; document.getElementById("sendButton").disabled = true;};
}


function sendUpdate(){
    sendToServer(controlsJSON());
}


function showMessage(message) {
    commandHistory = document.getElementById("commandHistory");
    commandHistory.textContent += `\n${message}`;
    commandHistory.scrollTop = commandHistory.scrollHeight;
    commandHistory.value = '';
}


var t=setInterval(sendUpdate, 40);
