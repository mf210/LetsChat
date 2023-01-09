


const notificationSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/notification/'
);

notificationSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const msgType = data['type'];
    console.log(`new message: ${msgType}`);
};

notificationSocket.onopen = function(e) {
    console.log('notification socket is open now!');
};

notificationSocket.onclose = function(e) {
    console.error('notification socket closed.');
};