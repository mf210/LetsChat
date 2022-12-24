const roomName = JSON.parse(document.getElementById('room-name').textContent);

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/groupchat/'
    + roomName
    + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    appendChatMessage(data);
};

chatSocket.onclose = function(e) {
    console.error('ChatSocket closed.');
};

chatSocket.onerror = function(e){
    console.log('ChatSocket error', e);
};

document.getElementById('id-chat-message-input').focus();
document.getElementById('id-chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13 && !e.shiftKey) {  // enter
        document.getElementById('id-chat-message-submit').click();
    }
};

document.querySelector('#id-chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#id-chat-message-input');
    const message = messageInputDom.value.trim();
    if (message) {
        chatSocket.send(JSON.stringify({
            command: 'send',
            message: message
        }));
    } else {
        showClientErrorModal("You can't send an empty message!");
    }
    messageInputDom.value = '';
};

function appendChatMessage(data){

    const msg = data['message'] + '\n';
    const username = data['username'] + ": ";
    const profileImageURL = data['profile_image_url'];
    const profileURL = data['profile_url'];

    // Create chat message element
    let chatLog = document.getElementById("id-chat-log");

    let newMessageDiv = document.createElement("div");
    newMessageDiv.classList.add('d-flex');
    newMessageDiv.classList.add('flex-row');
    newMessageDiv.classList.add('message-container');
    
    let profileImage = document.createElement('img');
    profileImage.addEventListener('click', (e) => window.open(profileURL, '_blank'));
    profileImage.classList.add('profile-image');
    profileImage.classList.add('rounded-circle');
    profileImage.classList.add('img-flui');
    profileImage.src = profileImageURL;
    newMessageDiv.appendChild(profileImage);

    let div1 = document.createElement('div');
    div1.classList.add('d-flex');
    div1.classList.add('flex-column');

    let div2 = document.createElement('div');
    div2.classList.add('d-flex');
    div2.classList.add('flex-row');

    let usernameSpan = document.createElement('span');
    usernameSpan.addEventListener('click', (e) => window.open(profileURL, '_blank'));
    usernameSpan.classList.add('username-span');
    usernameSpan.innerHTML = username;
    div2.appendChild(usernameSpan);

    div1.appendChild(div2);

    let msgP = document.createElement('p');
    msgP.innerHTML = msg;
    msgP.classList.add('msg-p');
    div1.appendChild(msgP);

    newMessageDiv.appendChild(div1);

    chatLog.insertBefore(newMessageDiv, chatLog.firstChild);
};

function showClientErrorModal(message){
    document.getElementById("error-modal-body").innerHTML = message;
    document.getElementById("modal-button").click();
};
