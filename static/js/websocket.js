// MDN WebSocket documentation
// https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

window.onload = () => {

	const socket = new WebSocket('wss://0gsc0sffqf.execute-api.ap-southeast-1.amazonaws.com/production')

	socketBody = {'accountRole': 'admin', 'username': '0rang3'}

	socket.addEventListener('open', e => {
		console.log('WebSocket is connected')
		socket.send(JSON.stringify(socketBody))
		console.log("Hi")
	})

	socket.addEventListener('close', e => console.log('WebSocket is closed'))

	socket.addEventListener('error', e => console.error('WebSocket is in error', e))

	socket.addEventListener('message', e => {
		// Web socket received message
		// HTML element for bade allows for display of red exclamaiton mark to direct user to announcement/clarification pages
		data = JSON.parse(e.data)
		if (data.notificationType === 'announce'){
			var badge=document.getElementById('admin_badge');
			if(badge!=null){
				badge.hidden=false;
				alert("New announcement!");
			}
			console.log('Announcement!')
		}else if (data.notificationType == 'newclarification'){
			var badge=document.getElementById('clarification_badge');
			var badge=document.getElementById('admin_badge');
			if(badge!=null){
				badge.hidden=false;
				alert("New clarification!");
			}
			console.log('Clarification!')
		}else if (data.notifcationType == 'answeredclarification'){
			var badge=document.getElementById('clarification_badge');
			if(badge!=null){
				badge.hidden=false;
				alert("Your clarification has been answered!");
			}
		}else{
			console.log('WebSocket Error')
		}
	})
}