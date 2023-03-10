let ws;

function send(data) {
    if (!ws){
	//showMessage("No Websocket connection")
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

    //ws           = new WebSocket('ws://localhost:9000');
    ws           = new WebSocket('ws://10.0.0.17:9000');
    ws.onopen    = () => { document.getElementById("sendButton").disabled = false; };
    ws.onmessage = ({ data }) => showMessage(data);//showMessage(data);
    ws.onclose   = function() { ws = null; document.getElementById("sendButton").disabled = true;};
}


class JoystickController
{
    constructor( joystickID, maxDistance, deadzone ){	
	this.id        = joystickID;
	this.dragStart = null;
	this.touchId   = null;
	this.active    = false;
	this.value     = { x: 0, y: 0 }; 
	
	let self       = this;

	function handleDown(event){
	    self.active            = true;
	    stick.style.transition = '0s';
	    event.preventDefault();

	    if (event.changedTouches)
		self.dragStart = { x: event.changedTouches[0].clientX, y: event.changedTouches[0].clientY };
	    else
		self.dragStart = { x: event.clientX, y: event.clientY };

	    if (event.changedTouches)
		self.touchId   = event.changedTouches[0].identifier;
	}

	
	function handleMove(event) {
	    if ( !self.active ) return;
	    
	    let touchmoveId = null;
	    
	    if (event.changedTouches)
	    {
		for (let i = 0; i < event.changedTouches.length; i++)
		{
		    if (self.touchId == event.changedTouches[i].identifier)
		    {
		    	touchmoveId   = i;
		    	event.clientX = event.changedTouches[i].clientX;
		    	event.clientY = event.changedTouches[i].clientY;
		    }
		}

		if (touchmoveId == null) return;
	    }

	    const xDiff     = event.clientX - self.dragStart.x;
	    const yDiff     = event.clientY - self.dragStart.y;
	    const angle     = Math.atan2(yDiff, xDiff);
	    const distance  = Math.min(maxDistance, Math.hypot(xDiff, yDiff));
	    const xPosition = distance * Math.cos(angle);
	    const yPosition = distance * Math.sin(angle);

	    stick.style.transform = `translate3d(${xPosition}px, ${yPosition}px, 0px)`;

	    const distance2  = (distance < deadzone) ? 0 : maxDistance / (maxDistance - deadzone) * (distance - deadzone);
	    const xPosition2 = distance2 * Math.cos(angle);
	    const yPosition2 = distance2 * Math.sin(angle);
	    const xPercent   = parseFloat((xPosition2 / maxDistance).toFixed(4));
	    const yPercent   = parseFloat((yPosition2 / maxDistance).toFixed(4));
	    
	    self.value = { x: xPercent, y: -yPercent };
	}

	function handleUp(event) {
	    if ( !self.active ) return;

	    if (event.changedTouches && self.touchId != event.changedTouches[0].identifier) return;

	    stick.style.transition = '.2s';
	    stick.style.transform  = `translate3d(0px, 0px, 0px)`;
	    self.value             = { x: 0, y: 0 };
	    self.touchId           = null;
	    self.active            = false;
	}

	let stick = document.getElementById(this.id);
	
	stick.addEventListener   ('mousedown',  handleDown);
	stick.addEventListener   ('touchstart', handleDown);
	document.addEventListener('mousemove',  handleMove, {passive: false});
	document.addEventListener('touchmove',  handleMove, {passive: false});
	document.addEventListener('mouseup',    handleUp);
	document.addEventListener('touchend',   handleUp);
	//update()
    }
}


class SliderController
{
    constructor( sliderID, maxDistance, deadzone ){
	this.id        = sliderID;
	this.dragStart = null;
	this.touchId   = null;
	this.active    = false;
	this.value     = { y: 0 }; 
	
	let self       = this;

	function handleDown(event)
	{
	    self.active            = true;
	    stick.style.transition = '0s';
	    event.preventDefault();

	    if (event.changedTouches)
		self.dragStart = { y: event.changedTouches[0].clientY };
	    else
		self.dragStart = { y: event.clientY };

	    if (event.changedTouches)
		self.touchId   = event.changedTouches[0].identifier;
	}

	
	function handleMove(event) 
	{
	    if ( !self.active ) return;
	    
	    let touchmoveId = null;
	    
	    if (event.changedTouches)
	    {
		for (let i = 0; i < event.changedTouches.length; i++)
		{
		    if (self.touchId == event.changedTouches[i].identifier)
		    {
		    	touchmoveId   = i;
		    	event.clientY = event.changedTouches[i].clientY;
		    }
		}	
		if (touchmoveId == null) return;
	    }

	    const yDiff     =  event.clientY - self.dragStart.y;
	    const distance  =  Math.max(-maxDistance, Math.min(maxDistance, yDiff));
	    const yPercent  = (Math.abs(distance) < deadzone) ? 0 : distance/maxDistance;
	    self.value      = { y: -yPercent };
	    
	    stick.style.transform = `translate3d(0px, ${distance}px, 0px)`;
	}

	function handleUp(event) 
	{
	    if ( !self.active ) return;

	    if (event.changedTouches && self.touchId != event.changedTouches[0].identifier) return;

	    stick.style.transition = '.2s';
	    stick.style.transform  = `translate3d(0px, 0px, 0px)`;
	    self.value             = { x: 0, y: 0 };
	    self.touchId           = null;
	    self.active            = false;
	}

	let stick = document.getElementById(this.id);
	
	stick.addEventListener   ('mousedown',  handleDown);
	stick.addEventListener   ('touchstart', handleDown);
	document.addEventListener('mousemove',  handleMove, {passive: false});
	document.addEventListener('touchmove',  handleMove, {passive: false});
	document.addEventListener('mouseup',    handleUp);
	document.addEventListener('touchend',   handleUp);
	//update();
    }
}


let joystick = new JoystickController("stick", 64, 8);
let slider   = new SliderController("slider", 64, 8);

function update()
{
    document.getElementById("joystick_x").innerText = "x: " + joystick.value.x;
    document.getElementById("joystick_y").innerText = "y: " + joystick.value.y;
    document.getElementById("slider_y").innerText   = "y: " + slider.value.y;
    message = {'joystick_x' : String(joystick.value.x),
	       'joystick_y' : String(joystick.value.y),
	       'slider_y'   : String(slider.value.y)
	      }
    
    send(JSON.stringify(message));
}

function sendCommand(){
    command       = document.getElementById("commandInput");
    message       = {'message' : command.value}
    command.value = "";
    send(JSON.stringify(message));
}

function showMessage(message) {
    commandHistory = document.getElementById("commandHistory");
    commandHistory.textContent += `\n${message}`;
    commandHistory.scrollTop = commandHistory.scrollHeight;
    commandHistory.value = '';
}

init();

var t=setInterval(update,40);
