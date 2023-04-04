
let ws;

function sendToServer(data) {
    if (!ws){
	console.log("No Websocket connection")
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

    wsAddress    = 'wss://' + serverIP + ':' + websocketPort;
    ws           = new WebSocket(wsAddress);//, { rejectUnauthorized: false });
    ws.onopen    = () => { document.getElementById("sendButton").disabled = false; };
    ws.onmessage = ({ data }) => showMessage(data);//showMessage(data);
    ws.onclose   = function() { ws = null; document.getElementById("sendButton").disabled = true;};
}
